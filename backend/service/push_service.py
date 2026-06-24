"""
多渠道推送统一适配器

支持：钉钉 / 飞书 / 企业微信 / 邮箱
"""

import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from db.models import PushConfig, DataSource


def push_to_channel(config: PushConfig, test_mode: bool = False, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """单渠道推送"""
    cfg = json.loads(config.config_json or "{}")

    if config.push_type == "dingtalk":
        return _push_dingtalk(cfg, file_path)
    elif config.push_type == "feishu":
        return _push_feishu(cfg, file_path)
    elif config.push_type == "wecom":
        return _push_wecom(cfg, file_path)
    elif config.push_type == "email":
        return _push_email(cfg, file_path)
    return False, f"未知推送类型: {config.push_type}"


def push_report_to_all_channels(source_id: int, file_path: str, db: Session) -> Tuple[bool, str]:
    """推送报表到数据源绑定的所有渠道"""
    configs = db.query(PushConfig).filter(
        PushConfig.source_id == source_id, PushConfig.is_enable == True
    ).all()

    if not configs:
        return False, "该数据源未配置推送渠道"

    success_count = 0
    for cfg in configs:
        try:
            ok, msg = push_to_channel(cfg, file_path=file_path)
            if ok:
                success_count += 1
        except Exception as e:
            pass

    return success_count > 0, f"推送完成: {success_count}/{len(configs)} 成功"


def _push_dingtalk(cfg: dict, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """钉钉群机器人推送"""
    webhook = cfg.get("webhook", "")
    secret = cfg.get("secret", "")

    if not webhook:
        return False, "未配置Webhook地址"

    content = "📊 PeerBizSync 报表已更新，请查看附件"
    data = {"msgtype": "text", "text": {"content": content}}

    try:
        resp = requests.post(webhook, json=data, timeout=10)
        resp.raise_for_status()
        return True, "钉钉推送成功"
    except Exception as e:
        return False, f"钉钉推送失败: {str(e)}"


def _push_feishu(cfg: dict, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """飞书推送"""
    webhook = cfg.get("webhook", "")
    if not webhook:
        return False, "未配置Webhook地址"
    content = "📊 PeerBizSync 报表已更新"
    data = {"msg_type": "text", "content": {"text": content}}
    try:
        resp = requests.post(webhook, json=data, timeout=10)
        resp.raise_for_status()
        return True, "飞书推送成功"
    except Exception as e:
        return False, f"飞书推送失败: {str(e)}"


def _push_wecom(cfg: dict, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """企业微信推送"""
    webhook = cfg.get("webhook", "")
    if not webhook:
        return False, "未配置Webhook地址"
    content = "📊 PeerBizSync 报表已更新"
    data = {"msgtype": "text", "text": {"content": content}}
    try:
        resp = requests.post(webhook, json=data, timeout=10)
        resp.raise_for_status()
        return True, "企业微信推送成功"
    except Exception as e:
        return False, f"企业微信推送失败: {str(e)}"


def _push_email(cfg: dict, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """SMTP 邮件推送（支持附件）"""
    smtp_server = cfg.get("smtp_server", "")
    smtp_port = int(cfg.get("smtp_port", 465))
    sender = cfg.get("sender", "")
    password = cfg.get("password", "")
    receivers = cfg.get("receivers", "")

    if not all([smtp_server, sender, password, receivers]):
        return False, "邮件配置不完整"

    msg = MIMEMultipart()
    msg["Subject"] = cfg.get("subject", "PeerBizSync 报表")
    msg["From"] = sender
    msg["To"] = receivers

    text = MIMEText("请查收附件中的数据报表。", "plain", "utf-8")
    msg.attach(text)

    # 附件
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(file_path)}"')
            msg.attach(part)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender, password)
                server.sendmail(sender, receivers.split(","), msg.as_string())
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receivers.split(","), msg.as_string())
        return True, "邮件推送成功"
    except Exception as e:
        return False, f"邮件推送失败: {str(e)}"
