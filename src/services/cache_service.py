"""
Image Caching Service for managing generated images
"""
import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class ImageCacheService:
    """Service for caching generated images to avoid redundant API calls"""

    def __init__(self, cache_dir: str = "cache/images", metadata_file: str = "cache/metadata.json"):
        self.cache_dir = Path(cache_dir)
        self.metadata_file = Path(metadata_file)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing metadata
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                return {}
        return {}

    def _save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _generate_cache_key(self, prompt: str, size: str = "1024x1024", model: str = "dall-e-3", quality: str = "standard") -> str:
        """Generate a unique cache key for the image parameters"""
        content = f"{prompt}_{size}_{model}_{quality}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cached image"""
        return self.cache_dir / f"{cache_key}.png"

    def _is_cache_valid(self, cache_entry: Dict[str, Any], max_age_days: int = 30) -> bool:
        """Check if a cache entry is still valid"""
        if "timestamp" not in cache_entry:
            return False

        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        max_age = timedelta(days=max_age_days)

        return datetime.now() - cache_time < max_age

    def get_cached_image(self, prompt: str, size: str = "1024x1024", model: str = "dall-e-3", quality: str = "standard") -> Optional[str]:
        """Get cached image path if it exists and is valid"""
        cache_key = self._generate_cache_key(prompt, size, model, quality)
        cache_path = self._get_cache_path(cache_key)

        # Check if file exists
        if not cache_path.exists():
            return None

        # Check cache metadata
        if cache_key not in self.metadata:
            logger.warning(f"Cache file exists but no metadata for key: {cache_key}")
            return None

        cache_entry = self.metadata[cache_key]

        # Check if cache is still valid
        if not self._is_cache_valid(cache_entry):
            logger.info(f"Cache entry expired for key: {cache_key}")
            self.remove_cached_image(cache_key)
            return None

        # Verify the cached file matches the expected parameters
        if (cache_entry.get("prompt") != prompt or
            cache_entry.get("size") != size or
            cache_entry.get("model") != model or
            cache_entry.get("quality") != quality):
            logger.warning(f"Cache entry parameters don't match for key: {cache_key}")
            return None

        logger.info(f"Using cached image: {cache_path}")
        return str(cache_path)

    def cache_image(self, image_path: str, prompt: str, size: str = "1024x1024",
                   model: str = "dall-e-3", quality: str = "standard") -> str:
        """Cache an image with its generation parameters"""
        cache_key = self._generate_cache_key(prompt, size, model, quality)
        cache_path = self._get_cache_path(cache_key)

        try:
            # Copy image to cache directory
            import shutil
            shutil.copy2(image_path, cache_path)

            # Update metadata
            self.metadata[cache_key] = {
                "prompt": prompt,
                "size": size,
                "model": model,
                "quality": quality,
                "timestamp": datetime.now().isoformat(),
                "original_path": image_path,
                "cache_path": str(cache_path)
            }

            self._save_metadata()

            logger.info(f"Image cached successfully: {cache_path}")
            return str(cache_path)

        except Exception as e:
            logger.error(f"Failed to cache image: {e}")
            return image_path  # Return original path if caching fails

    def remove_cached_image(self, cache_key: str):
        """Remove a cached image and its metadata"""
        try:
            # Remove file
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()

            # Remove metadata
            if cache_key in self.metadata:
                del self.metadata[cache_key]
                self._save_metadata()

            logger.info(f"Removed cached image: {cache_key}")

        except Exception as e:
            logger.error(f"Failed to remove cached image {cache_key}: {e}")

    def clear_expired_cache(self, max_age_days: int = 30):
        """Clear expired cache entries"""
        expired_keys = []

        for cache_key, entry in self.metadata.items():
            if not self._is_cache_valid(entry, max_age_days):
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            self.remove_cached_image(cache_key)

        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.metadata)
        total_size = 0
        expired_count = 0

        for cache_key, entry in self.metadata.items():
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                total_size += cache_path.stat().st_size
            else:
                expired_count += 1

            if not self._is_cache_valid(entry):
                expired_count += 1

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "expired_entries": expired_count,
            "cache_directory": str(self.cache_dir),
            "metadata_file": str(self.metadata_file)
        }

    def list_cache_entries(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """List all cache entries"""
        entries = []

        for cache_key, entry in self.metadata.items():
            cache_path = self._get_cache_path(cache_key)
            entry_info = {
                "cache_key": cache_key,
                "cache_path": str(cache_path),
                "file_exists": cache_path.exists(),
                "is_expired": not self._is_cache_valid(entry),
                **entry
            }

            if include_expired or not entry_info["is_expired"]:
                entries.append(entry_info)

        return sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)

    def cleanup_cache(self, max_age_days: int = 30, max_size_mb: int = 1000):
        """Clean up cache by removing expired entries and oldest files if over size limit"""
        # First, remove expired entries
        self.clear_expired_cache(max_age_days)

        # Check total size
        stats = self.get_cache_stats()
        if stats["total_size_mb"] <= max_size_mb:
            return

        # If still over size limit, remove oldest files
        entries = self.list_cache_entries(include_expired=False)
        entries.sort(key=lambda x: x.get("timestamp", ""))

        size_to_remove = stats["total_size_mb"] - max_size_mb
        removed_size = 0

        for entry in entries:
            if removed_size >= size_to_remove:
                break

            cache_key = entry["cache_key"]
            cache_path = self._get_cache_path(cache_key)

            if cache_path.exists():
                file_size_mb = cache_path.stat().st_size / (1024 * 1024)
                removed_size += file_size_mb

            self.remove_cached_image(cache_key)

        logger.info(f"Cache cleanup completed. Removed {removed_size:.2f} MB")


class ContentCacheService:
    """General-purpose content caching service"""

    def __init__(self, cache_dir: str = "cache/content"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key"""
        # Use hash of key to ensure valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached content"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            async with asyncio.Lock():  # Prevent concurrent access issues
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    return data.get("content")
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            logger.warning(f"Failed to read cache for key {key}: {e}")
            return None

    async def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Set cached content with TTL"""
        cache_path = self._get_cache_path(key)

        cache_data = {
            "content": value,
            "timestamp": datetime.now().isoformat(),
            "ttl_seconds": ttl_seconds,
            "expires_at": (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
        }

        try:
            async with asyncio.Lock():
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to write cache for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached content"""
        cache_path = self._get_cache_path(key)

        try:
            async with asyncio.Lock():
                if cache_path.exists():
                    cache_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        cache_path = self._get_cache_path(key)
        return cache_path.exists()

    async def is_expired(self, key: str) -> bool:
        """Check if cached content is expired"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return True

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)

            expires_at = datetime.fromisoformat(data.get("expires_at", ""))
            return datetime.now() > expires_at

        except (json.JSONDecodeError, FileNotFoundError, KeyError, ValueError) as e:
            logger.warning(f"Failed to check expiration for key {key}: {e}")
            return True
