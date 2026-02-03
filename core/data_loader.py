"""CSV data loading and validation for Sophos firewall logs."""
import pandas as pd
from pathlib import Path


class FirewallDataLoader:
    """Loads and validates Sophos firewall CSV data."""
    
    REQUIRED_COLUMNS = [
        'Source IP',
        'Destination IP',
        'Hits',
        'Source Country',
        'Classification'
    ]
    
    def __init__(self, csv_file):
        """
        Initialize loader with CSV file path.
        
        Args:
            csv_file: Path to Sophos firewall CSV export
        """
        self.csv_file = Path(csv_file)
        self.df = None
    
    def load(self):
        """
        Load CSV file and validate required columns.
        
        Returns:
            pandas.DataFrame: Loaded firewall data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        print(f"Loading Sophos logs: {self.csv_file}")
        self.df = pd.read_csv(self.csv_file)
        
        # Validate required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        print(f"Loaded {len(self.df)} log entries")
        return self.df
