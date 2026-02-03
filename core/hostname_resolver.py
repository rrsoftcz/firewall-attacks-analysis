"""Hostname resolution with caching and parallel processing."""
import socket
import json
import ipaddress
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


class HostnameResolver:
    """Resolves IP addresses to hostnames with intelligent caching."""
    
    def __init__(self, cache_file='.hostname_cache.json', cache_ttl_days=7):
        """
        Initialize hostname resolver.
        
        Args:
            cache_file: Path to cache file
            cache_ttl_days: Cache time-to-live in days
        """
        self.cache_file = Path(cache_file)
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.cache = self._load_cache()
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'resolved': 0,
            'failed': 0
        }
    
    def _load_cache(self):
        """Load hostname cache from file."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Filter out expired entries
            now = datetime.now()
            valid_cache = {}
            for ip, entry in cache_data.items():
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if now - cached_time < self.cache_ttl:
                    valid_cache[ip] = entry
            
            return valid_cache
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            return {}
    
    def _save_cache(self):
        """Save hostname cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    @staticmethod
    def is_internal_ip(ip_str):
        """
        Check if IP is internal/private.
        
        Args:
            ip_str: IP address string
            
        Returns:
            bool: True if internal IP
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private
        except ValueError:
            return False
    
    def _resolve_single(self, ip, timeout=1.0):
        """
        Resolve single IP to hostname.
        
        Args:
            ip: IP address string
            timeout: DNS timeout in seconds
            
        Returns:
            str: Hostname or original IP if resolution fails
        """
        # Check cache first
        if ip in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[ip]['hostname']
        
        self.stats['cache_misses'] += 1
        
        # Attempt DNS resolution
        try:
            socket.setdefaulttimeout(timeout)
            hostname = socket.gethostbyaddr(ip)[0]
            
            # Cache successful resolution
            self.cache[ip] = {
                'hostname': hostname,
                'timestamp': datetime.now().isoformat(),
                'type': 'internal' if self.is_internal_ip(ip) else 'external'
            }
            self.stats['resolved'] += 1
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout, OSError):
            # Cache failed resolution to avoid retries
            self.cache[ip] = {
                'hostname': ip,  # Fallback to IP
                'timestamp': datetime.now().isoformat(),
                'type': 'internal' if self.is_internal_ip(ip) else 'external',
                'failed': True
            }
            self.stats['failed'] += 1
            return ip
    
    def resolve_batch(self, ip_list, max_workers=50, timeout=1.0, 
                     internal_only=False, show_progress=True):
        """
        Resolve multiple IPs in parallel.
        
        Args:
            ip_list: List of IP addresses
            max_workers: Number of parallel workers
            timeout: DNS timeout per IP
            internal_only: Only resolve internal IPs
            show_progress: Show progress output
            
        Returns:
            dict: IP -> hostname mapping
        """
        # Filter unique IPs
        unique_ips = list(set(ip_list))
        
        # Filter internal-only if requested
        if internal_only:
            unique_ips = [ip for ip in unique_ips if self.is_internal_ip(ip)]
        
        if show_progress:
            print(f"Resolving {len(unique_ips)} unique IP addresses...")
        
        # Resolve in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ip = {
                executor.submit(self._resolve_single, ip, timeout): ip 
                for ip in unique_ips
            }
            
            # Collect results
            completed = 0
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    hostname = future.result()
                    results[ip] = hostname
                    
                    completed += 1
                    if show_progress and completed % 100 == 0:
                        print(f"  Progress: {completed}/{len(unique_ips)} IPs processed...")
                except Exception as e:
                    results[ip] = ip  # Fallback
                    print(f"  Error resolving {ip}: {e}")
        
        # Save updated cache
        self._save_cache()
        
        if show_progress:
            print(f"Resolution complete!")
            print(f"  Cache hits: {self.stats['cache_hits']}")
            print(f"  New resolutions: {self.stats['resolved']}")
            print(f"  Failed: {self.stats['failed']}")
        
        return results
    
    def get_hostname(self, ip):
        """
        Get hostname for single IP (uses cache).
        
        Args:
            ip: IP address string
            
        Returns:
            str: Hostname or IP if not cached
        """
        if ip in self.cache:
            return self.cache[ip]['hostname']
        return ip
    
    def enrich_dataframe(self, df, ip_columns=['Source IP', 'Destination IP'],
                        max_workers=50, timeout=1.0, internal_only=False):
        """
        Add hostname columns to DataFrame.
        
        Args:
            df: pandas DataFrame
            ip_columns: List of column names containing IPs
            max_workers: Parallel workers
            timeout: DNS timeout
            internal_only: Only resolve internal IPs
            
        Returns:
            pandas DataFrame with added hostname columns
        """
        # Collect all IPs to resolve
        all_ips = []
        for col in ip_columns:
            if col in df.columns:
                all_ips.extend(df[col].unique().tolist())
        
        # Resolve in batch
        hostname_map = self.resolve_batch(
            all_ips, 
            max_workers=max_workers,
            timeout=timeout,
            internal_only=internal_only
        )
        
        # Add hostname columns
        for col in ip_columns:
            if col in df.columns:
                hostname_col = f"{col} Hostname"
                df[hostname_col] = df[col].map(
                    lambda ip: hostname_map.get(ip, ip)
                )
        
        return df
    
    def clear_cache(self):
        """Clear hostname cache."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("Hostname cache cleared")
    
    def get_cache_stats(self):
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics
        """
        total = len(self.cache)
        internal = sum(1 for e in self.cache.values() if e.get('type') == 'internal')
        external = sum(1 for e in self.cache.values() if e.get('type') == 'external')
        failed = sum(1 for e in self.cache.values() if e.get('failed', False))
        
        return {
            'total_cached': total,
            'internal_ips': internal,
            'external_ips': external,
            'failed_resolutions': failed,
            'cache_file': str(self.cache_file),
            'cache_file_exists': self.cache_file.exists()
        }
