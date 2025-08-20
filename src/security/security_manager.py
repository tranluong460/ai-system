"""
Security & Privacy Manager cho AI Assistant
"""
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import bcrypt

class EncryptionManager:
    """Quản lý encryption cho dữ liệu nhạy cảm"""
    
    def __init__(self, data_dir: str = "data/security"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.key_file = os.path.join(data_dir, "encryption.key")
        self.salt_file = os.path.join(data_dir, "salt.key")
        
        # Initialize encryption
        self.salt = self._get_or_create_salt()
        self.fernet = None
        
        print("🔐 Encryption Manager initialized")
    
    def _get_or_create_salt(self) -> bytes:
        """Lấy hoặc tạo salt cho key derivation"""
        try:
            if os.path.exists(self.salt_file):
                with open(self.salt_file, 'rb') as f:
                    return f.read()
            else:
                salt = os.urandom(16)
                with open(self.salt_file, 'wb') as f:
                    f.write(salt)
                return salt
        except Exception as e:
            print(f"❌ Salt error: {e}")
            return os.urandom(16)
    
    def set_password(self, password: str):
        """Đặt password và tạo encryption key"""
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Initialize Fernet
            self.fernet = Fernet(key)
            
            # Save encrypted key file
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            print("✅ Encryption password set")
            return True
        except Exception as e:
            print(f"❌ Password setting error: {e}")
            return False
    
    def load_encryption_key(self, password: str) -> bool:
        """Load encryption key với password"""
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Test if key works
            self.fernet = Fernet(key)
            
            # Test encryption/decryption
            test_data = b"test"
            encrypted = self.fernet.encrypt(test_data)
            decrypted = self.fernet.decrypt(encrypted)
            
            if decrypted != test_data:
                raise Exception("Key verification failed")
            
            print("✅ Encryption key loaded")
            return True
        except Exception as e:
            print(f"❌ Key loading error: {e}")
            self.fernet = None
            return False
    
    def encrypt_data(self, data: Union[str, dict, list]) -> Optional[bytes]:
        """Encrypt dữ liệu"""
        if not self.fernet:
            print("❌ Encryption not initialized")
            return None
        
        try:
            # Convert to string if needed
            if isinstance(data, (dict, list)):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
            
            # Encrypt
            encrypted = self.fernet.encrypt(data.encode('utf-8'))
            return encrypted
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return None
    
    def decrypt_data(self, encrypted_data: bytes) -> Optional[str]:
        """Decrypt dữ liệu"""
        if not self.fernet:
            print("❌ Encryption not initialized")
            return None
        
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> Optional[str]:
        """Encrypt file"""
        if not self.fernet:
            return None
        
        try:
            if not output_path:
                output_path = file_path + ".encrypted"
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.fernet.encrypt(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return output_path
        except Exception as e:
            print(f"❌ File encryption error: {e}")
            return None
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> Optional[str]:
        """Decrypt file"""
        if not self.fernet:
            return None
        
        try:
            if not output_path:
                output_path = encrypted_file_path.replace(".encrypted", "")
            
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
        except Exception as e:
            print(f"❌ File decryption error: {e}")
            return None

class PermissionSystem:
    """Hệ thống phân quyền"""
    
    def __init__(self, data_dir: str = "data/security"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.permissions_file = os.path.join(data_dir, "permissions.json")
        self.roles_file = os.path.join(data_dir, "roles.json")
        
        # Default permissions
        self.default_permissions = {
            "read_conversations": True,
            "write_conversations": True,
            "delete_conversations": False,
            "access_memory": True,
            "modify_memory": True,
            "export_data": True,
            "import_data": False,
            "system_commands": False,
            "file_operations": True,
            "network_access": True,
            "camera_access": False,
            "microphone_access": False,
            "location_access": False,
            "calendar_access": True,
            "mood_tracking": True,
            "screenshot_capture": False,
            "automation_workflows": True,
            "ai_model_access": True,
            "encryption_management": False
        }
        
        # Load permissions
        self.permissions = self._load_permissions()
        self.roles = self._load_roles()
        
        print("🛡️ Permission System initialized")
    
    def _load_permissions(self) -> Dict[str, bool]:
        """Load user permissions"""
        try:
            if os.path.exists(self.permissions_file):
                with open(self.permissions_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    permissions = self.default_permissions.copy()
                    permissions.update(loaded)
                    return permissions
        except Exception as e:
            print(f"❌ Error loading permissions: {e}")
        
        return self.default_permissions.copy()
    
    def _save_permissions(self):
        """Save permissions"""
        try:
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(self.permissions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving permissions: {e}")
    
    def _load_roles(self) -> Dict[str, Dict[str, bool]]:
        """Load role definitions"""
        default_roles = {
            "basic_user": {
                "read_conversations": True,
                "write_conversations": True,
                "access_memory": True,
                "file_operations": False,
                "system_commands": False,
                "encryption_management": False
            },
            "power_user": {
                "read_conversations": True,
                "write_conversations": True,
                "access_memory": True,
                "modify_memory": True,
                "file_operations": True,
                "export_data": True,
                "automation_workflows": True,
                "system_commands": False,
                "encryption_management": False
            },
            "admin": {
                **{k: True for k in self.default_permissions.keys()}
            }
        }
        
        try:
            if os.path.exists(self.roles_file):
                with open(self.roles_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_roles.update(loaded)
        except Exception as e:
            print(f"❌ Error loading roles: {e}")
        
        return default_roles
    
    def check_permission(self, permission: str) -> bool:
        """Kiểm tra permission"""
        return self.permissions.get(permission, False)
    
    def request_permission(self, permission: str, reason: str = "") -> bool:
        """Request permission từ user"""
        if self.check_permission(permission):
            return True
        
        print(f"🔐 Permission required: {permission}")
        if reason:
            print(f"Reason: {reason}")
        
        # Simple CLI permission request
        response = input(f"Grant permission '{permission}'? (y/n): ").lower()
        granted = response == 'y'
        
        if granted:
            self.permissions[permission] = True
            self._save_permissions()
            print(f"✅ Permission '{permission}' granted")
        else:
            print(f"❌ Permission '{permission}' denied")
        
        return granted
    
    def set_permissions(self, permissions: Dict[str, bool]):
        """Set multiple permissions"""
        self.permissions.update(permissions)
        self._save_permissions()
        print("🛡️ Permissions updated")
    
    def apply_role(self, role_name: str) -> bool:
        """Apply role permissions"""
        if role_name not in self.roles:
            print(f"❌ Role '{role_name}' not found")
            return False
        
        role_permissions = self.roles[role_name]
        self.permissions.update(role_permissions)
        self._save_permissions()
        
        print(f"✅ Role '{role_name}' applied")
        return True
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt permissions"""
        granted_count = sum(1 for v in self.permissions.values() if v)
        total_count = len(self.permissions)
        
        return {
            "granted_permissions": granted_count,
            "total_permissions": total_count,
            "permission_coverage": (granted_count / total_count) * 100,
            "permissions": self.permissions,
            "available_roles": list(self.roles.keys())
        }

class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, data_dir: str = "data/security"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.audit_file = os.path.join(data_dir, "audit_log.json")
        self.session_id = secrets.token_hex(8)
        
        # Log levels
        self.LOG_LEVELS = {
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "SECURITY": 4,
            "CRITICAL": 5
        }
        
        # Start session
        self.log_event("SESSION_START", "info", {"session_id": self.session_id})
        
        print("📝 Audit Logger initialized")
    
    def log_event(self, event_type: str, level: str, details: Dict[str, Any] = None):
        """Log audit event"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "event_type": event_type,
                "level": level.upper(),
                "details": details or {},
                "source": "ai_assistant"
            }
            
            # Load existing logs
            logs = []
            if os.path.exists(self.audit_file):
                try:
                    with open(self.audit_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            # Add new log
            logs.append(log_entry)
            
            # Keep only last 10000 logs
            if len(logs) > 10000:
                logs = logs[-10000:]
            
            # Save logs
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            # Print security/critical events
            if level.upper() in ["SECURITY", "CRITICAL", "ERROR"]:
                print(f"🚨 {level.upper()}: {event_type} - {details}")
                
        except Exception as e:
            print(f"❌ Audit logging error: {e}")
    
    def log_user_action(self, action: str, resource: str = "", result: str = "success"):
        """Log user action"""
        self.log_event("USER_ACTION", "info", {
            "action": action,
            "resource": resource,
            "result": result
        })
    
    def log_permission_check(self, permission: str, granted: bool, reason: str = ""):
        """Log permission check"""
        self.log_event("PERMISSION_CHECK", "security", {
            "permission": permission,
            "granted": granted,
            "reason": reason
        })
    
    def log_data_access(self, data_type: str, operation: str, success: bool):
        """Log data access"""
        level = "info" if success else "warning"
        self.log_event("DATA_ACCESS", level, {
            "data_type": data_type,
            "operation": operation,
            "success": success
        })
    
    def log_security_incident(self, incident_type: str, details: Dict[str, Any]):
        """Log security incident"""
        self.log_event("SECURITY_INCIDENT", "critical", {
            "incident_type": incident_type,
            **details
        })
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Lấy audit summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            logs = []
            if os.path.exists(self.audit_file):
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    all_logs = json.load(f)
                    
                    for log in all_logs:
                        try:
                            log_time = datetime.fromisoformat(log["timestamp"])
                            if log_time >= cutoff_time:
                                logs.append(log)
                        except:
                            continue
            
            # Analyze logs
            event_counts = {}
            level_counts = {}
            
            for log in logs:
                event_type = log.get("event_type", "unknown")
                level = log.get("level", "unknown")
                
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                level_counts[level] = level_counts.get(level, 0) + 1
            
            return {
                "period_hours": hours,
                "total_events": len(logs),
                "event_types": event_counts,
                "log_levels": level_counts,
                "session_id": self.session_id
            }
            
        except Exception as e:
            print(f"❌ Audit summary error: {e}")
            return {}

class SecurityManager:
    """Main Security Manager"""
    
    def __init__(self, data_dir: str = "data/security"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize components
        self.encryption = EncryptionManager(data_dir)
        self.permissions = PermissionSystem(data_dir)
        self.audit = AuditLogger(data_dir)
        
        # Security settings
        self.settings_file = os.path.join(data_dir, "security_settings.json")
        self.settings = self._load_security_settings()
        
        print("🛡️ Security Manager initialized")
    
    def _load_security_settings(self) -> Dict[str, Any]:
        """Load security settings"""
        default_settings = {
            "encryption_enabled": False,
            "audit_logging": True,
            "permission_prompts": True,
            "auto_encrypt_sensitive": True,
            "session_timeout_minutes": 60,
            "max_failed_attempts": 3,
            "require_password_for_export": True,
            "data_retention_days": 90
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except Exception as e:
            print(f"❌ Error loading security settings: {e}")
        
        return default_settings
    
    def _save_security_settings(self):
        """Save security settings"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving security settings: {e}")
    
    def initialize_encryption(self, password: str) -> bool:
        """Initialize encryption với password"""
        success = self.encryption.set_password(password)
        if success:
            self.settings["encryption_enabled"] = True
            self._save_security_settings()
            self.audit.log_event("ENCRYPTION_INITIALIZED", "security")
        return success
    
    def secure_operation(self, operation_name: str, permission_required: str, 
                        operation_func, *args, **kwargs):
        """Thực hiện operation với security checks"""
        # Log the attempt
        self.audit.log_user_action(operation_name, kwargs.get("resource", ""))
        
        # Check permission
        if not self.permissions.check_permission(permission_required):
            if self.settings["permission_prompts"]:
                granted = self.permissions.request_permission(
                    permission_required, 
                    f"Required for {operation_name}"
                )
                if not granted:
                    self.audit.log_permission_check(permission_required, False, "user_denied")
                    raise PermissionError(f"Permission denied: {permission_required}")
            else:
                self.audit.log_permission_check(permission_required, False, "not_granted")
                raise PermissionError(f"Permission not granted: {permission_required}")
        
        self.audit.log_permission_check(permission_required, True)
        
        try:
            # Execute operation
            result = operation_func(*args, **kwargs)
            self.audit.log_user_action(operation_name, kwargs.get("resource", ""), "success")
            return result
        except Exception as e:
            self.audit.log_user_action(operation_name, kwargs.get("resource", ""), "failed")
            self.audit.log_event("OPERATION_FAILED", "error", {
                "operation": operation_name,
                "error": str(e)
            })
            raise
    
    def encrypt_sensitive_data(self, data: Any, data_type: str = "general") -> Optional[bytes]:
        """Encrypt sensitive data"""
        if not self.settings["encryption_enabled"]:
            return None
        
        encrypted = self.encryption.encrypt_data(data)
        if encrypted:
            self.audit.log_data_access(data_type, "encrypt", True)
        else:
            self.audit.log_data_access(data_type, "encrypt", False)
        
        return encrypted
    
    def decrypt_sensitive_data(self, encrypted_data: bytes, data_type: str = "general") -> Optional[str]:
        """Decrypt sensitive data"""
        if not self.settings["encryption_enabled"]:
            return None
        
        decrypted = self.encryption.decrypt_data(encrypted_data)
        if decrypted:
            self.audit.log_data_access(data_type, "decrypt", True)
        else:
            self.audit.log_data_access(data_type, "decrypt", False)
        
        return decrypted
    
    def get_security_status(self) -> Dict[str, Any]:
        """Lấy security status"""
        audit_summary = self.audit.get_audit_summary(24)
        permission_summary = self.permissions.get_permission_summary()
        
        return {
            "encryption_enabled": self.settings["encryption_enabled"],
            "audit_logging": self.settings["audit_logging"],
            "permission_system": permission_summary,
            "audit_summary_24h": audit_summary,
            "security_settings": self.settings,
            "session_id": self.audit.session_id
        }
    
    def update_security_settings(self, new_settings: Dict[str, Any]):
        """Update security settings"""
        self.settings.update(new_settings)
        self._save_security_settings()
        self.audit.log_event("SECURITY_SETTINGS_UPDATED", "security", new_settings)
        print("🛡️ Security settings updated")