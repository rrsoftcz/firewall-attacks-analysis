"""Risk report generation for high-risk attackers."""
import pandas as pd


class RiskReporter:
    """Generates risk reports from firewall data."""
    
    def __init__(self, dataframe):
        """
        Initialize reporter with cleaned dataframe.
        
        Args:
            dataframe: Cleaned pandas DataFrame
        """
        self.df = dataframe
    
    def generate_risk_report(self, output_file='high_risk_attackers.csv'):
        """
        Generate risk report CSV sorted by risk score.
        
        Risk Score = Total Hits + (Unique Targets × 10)
        This penalizes network scanners that hit many targets.
        
        Args:
            output_file: Output CSV filename
            
        Returns:
            pandas.DataFrame: Risk report data
        """
        risk_report = self.df.groupby('Source IP').agg({
            'Hits': 'sum',
            'Destination IP': 'nunique',
            'Source Country': 'first',
            'Classification': lambda x: x.mode()[0] if not x.empty else "Misc"
        }).reset_index()
        
        # Calculate risk score
        risk_report['Risk Score'] = (
            risk_report['Hits'] + (risk_report['Destination IP'] * 10)
        )
        
        # Sort by risk score descending
        risk_report = risk_report.sort_values(by='Risk Score', ascending=False)
        
        # Save to CSV
        risk_report.to_csv(output_file, index=False)
        print(f"Risk report: {output_file} ({len(risk_report)} attackers)")
        
        return risk_report
    
    def get_top_attackers(self, risk_report, n=10):
        """
        Get top N attackers for firewall blocking.
        
        Args:
            risk_report: Risk report DataFrame
            n: Number of top attackers to return
            
        Returns:
            list: List of top attacker IP addresses
        """
        return risk_report.head(n)['Source IP'].tolist()
