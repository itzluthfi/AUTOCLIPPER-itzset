"""
Configuration manager for YT Short Clipper
"""

import json
import uuid
from pathlib import Path


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: Path, output_dir: Path):
        self.config_file = config_file
        self.output_dir = output_dir
        self.config = self.load()
    
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                config = json.load(f)
                
                # Migrate old config to new multi-provider structure
                if "api_key" in config and "ai_providers" not in config:
                    config = self._migrate_to_multi_provider(config)
                
                # Add default system_prompt if not exists
                if "system_prompt" not in config:
                    from clipper_core import AutoClipperCore
                    config["system_prompt"] = AutoClipperCore.get_default_prompt()
                # Add default temperature if not exists
                if "temperature" not in config:
                    config["temperature"] = 1.0
                # Add default tts_model if not exists (for backward compatibility)
                if "tts_model" not in config:
                    config["tts_model"] = "tts-1"
                # Add default watermark settings if not exists
                if "watermark" not in config:
                    config["watermark"] = {
                        "enabled": False,
                        "image_path": "",
                        "position_x": 0.85,  # 0-1 (percentage from left)
                        "position_y": 0.05,  # 0-1 (percentage from top)
                        "opacity": 0.8,      # 0-1
                        "scale": 0.15        # 0-1 (percentage of video width)
                    }
                # Add default face tracking mode if not exists
                if "face_tracking_mode" not in config:
                    config["face_tracking_mode"] = "opencv"  # "opencv" or "mediapipe"
                # Add default MediaPipe settings if not exists
                if "mediapipe_settings" not in config:
                    config["mediapipe_settings"] = {
                        "lip_activity_threshold": 0.15,
                        "switch_threshold": 0.3,
                        "min_shot_duration": 90,
                        "center_weight": 0.3
                    }
                # Generate installation_id if not exists
                if "installation_id" not in config:
                    config["installation_id"] = str(uuid.uuid4())
                    self.save_config(config)
                
                # Ensure ai_providers structure exists
                if "ai_providers" not in config:
                    config["ai_providers"] = self._get_default_ai_providers()
                    self.save_config(config)
                
                # Add default Repliz settings if not exists
                if "repliz" not in config:
                    config["repliz"] = {
                        "access_key": "",
                        "secret_key": ""
                    }
                
                # Add default GPU settings if not exists
                if "gpu_acceleration" not in config:
                    config["gpu_acceleration"] = {
                        "enabled": False
                    }
                
                return config
        
        # Default config with system prompt
        from clipper_core import AutoClipperCore
        config = {
            "api_key": "",  # Kept for backward compatibility
            "base_url": "https://api.openai.com/v1",  # Kept for backward compatibility
            "model": "gpt-4.1",  # Kept for backward compatibility
            "tts_model": "tts-1",  # Kept for backward compatibility
            "temperature": 1.0,
            "output_dir": str(self.output_dir),
            "system_prompt": AutoClipperCore.get_default_prompt(),
            "installation_id": str(uuid.uuid4()),
            "ai_providers": self._get_default_ai_providers(),
            "watermark": {
                "enabled": False,
                "image_path": "",
                "position_x": 0.85,
                "position_y": 0.05,
                "opacity": 0.8,
                "scale": 0.15
            },
            "face_tracking_mode": "opencv",
            "mediapipe_settings": {
                "lip_activity_threshold": 0.15,
                "switch_threshold": 0.3,
                "min_shot_duration": 90,
                "center_weight": 0.3
            },
            "repliz": {
                "access_key": "",
                "secret_key": ""
            },
            "gpu_acceleration": {
                "enabled": False
            }
        }
        self.save_config(config)
        return config
    
    def _get_default_ai_providers(self):
        """Get default AI provider configuration"""
        return {
            "highlight_finder": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4.1"
            },
            "caption_maker": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "whisper-1"
            },
            "hook_maker": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "tts-1"
            },
            "youtube_title_maker": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4.1"
            }
        }
    
    def _migrate_to_multi_provider(self, old_config):
        """Migrate old single-provider config to new multi-provider structure"""
        api_key = old_config.get("api_key", "")
        base_url = old_config.get("base_url", "https://api.openai.com/v1")
        model = old_config.get("model", "gpt-4.1")
        tts_model = old_config.get("tts_model", "tts-1")
        
        old_config["ai_providers"] = {
            "highlight_finder": {
                "base_url": base_url,
                "api_key": api_key,
                "model": model
            },
            "caption_maker": {
                "base_url": base_url,
                "api_key": api_key,
                "model": "whisper-1"
            },
            "hook_maker": {
                "base_url": base_url,
                "api_key": api_key,
                "model": tts_model
            },
            "youtube_title_maker": {
                "base_url": base_url,
                "api_key": api_key,
                "model": model
            }
        }
        
        return old_config

    def save(self):
        """Save configuration to file"""
        self.save_config(self.config)
    
    def save_config(self, config):
        """Save configuration dict to file"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save"""
        self.config[key] = value
        self.save()
