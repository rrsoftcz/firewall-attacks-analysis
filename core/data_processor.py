"""Data cleaning, normalization, and aggregation for firewall logs."""
import pandas as pd


class FirewallDataProcessor:
    """Processes and aggregates firewall log data."""
    
    def __init__(self, dataframe):
        """
        Initialize processor with loaded dataframe.
        
        Args:
            dataframe: pandas DataFrame with firewall logs
        """
        self.df = dataframe.copy()
    
    def clean(self):
        """
        Clean and normalize data.
        
        Returns:
            self: For method chaining
        """
        # Normalize hits to numeric, fill missing with 1
        self.df['Hits'] = pd.to_numeric(self.df['Hits'], errors='coerce').fillna(1)
        
        # Strip whitespace from IP addresses
        self.df['Source IP'] = self.df['Source IP'].astype(str).str.strip()
        self.df['Destination IP'] = self.df['Destination IP'].astype(str).str.strip()
        
        return self
    
    def aggregate_for_visualization(self, top_n=None):
        """
        Aggregate data by Source IP -> Destination IP pairs.
        
        Args:
            top_n: Optional limit to top N connections by hits
            
        Returns:
            pandas.DataFrame: Aggregated connection data
        """
        aggregated = self.df.groupby(['Source IP', 'Destination IP']).agg({
            'Hits': 'sum',
            'Source Country': 'first',
            'Classification': 'first'
        }).reset_index()
        
        if top_n:
            aggregated = aggregated.nlargest(top_n, 'Hits')
        
        return aggregated
    
    def calculate_attacker_stats(self, aggregated_df):
        """
        Calculate statistics per attacker (Source IP).
        
        Args:
            aggregated_df: Aggregated dataframe from aggregate_for_visualization()
            
        Returns:
            pandas.Series: Total hits per source IP
        """
        return aggregated_df.groupby('Source IP')['Hits'].sum()
    
    def calculate_target_stats(self, aggregated_df):
        """
        Calculate statistics per target (Destination IP).
        
        Args:
            aggregated_df: Aggregated dataframe from aggregate_for_visualization()
            
        Returns:
            pandas.Series: Total hits per destination IP
        """
        return aggregated_df.groupby('Destination IP')['Hits'].sum()
