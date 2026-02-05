import pandas as pd
import re
import os

class PortfolioFileParser:
    """Parse portfolio files from CSV or Excel with various formats"""
    
    COLUMN_MAPPINGS = {
        'Stock Name': ['stock name', 'stock', 'symbol', 'scrip', 'name', 'security', 'stock_name', 'stockname', 'isin'],
        'Buy Price': ['buy price', 'buyprice', 'buy_price', 'price', 'purchase price', 'avg price', 'average price', 'avgprice', 'avg_price', 'cost'],
        'Buy Date': ['buy date', 'buydate', 'buy_date', 'date', 'purchase date', 'purchasedate', 'purchase_date', 'trade date', 'tradedate'],
        'Quantity': ['quantity', 'qty', 'shares', 'units', 'no of shares', 'number of shares', 'num_shares']
    }
    
    def __init__(self):
        self._isin_mappings = None
    
    @property
    def isin_mappings(self):
        if self._isin_mappings is None:
            try:
                from utils.database import Database
                db = Database()
                self._isin_mappings = db.get_isin_mappings()
            except Exception:
                self._isin_mappings = {}
        return self._isin_mappings
    
    def parse_file(self, uploaded_file):
        """Parse uploaded file and return normalized DataFrame"""
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel file.")
        
        df = self._normalize_columns(df)
        df = self._convert_isin_to_symbols(df)
        df = self._clean_data(df)
        
        return df
    
    def _normalize_columns(self, df):
        """Normalize column names to standard format"""
        df.columns = [col.strip() for col in df.columns]
        
        normalized_df = pd.DataFrame()
        original_columns = {col.lower().strip(): col for col in df.columns}
        
        for standard_name, variations in self.COLUMN_MAPPINGS.items():
            for variation in variations:
                variation_lower = variation.lower()
                if variation_lower in original_columns:
                    original_col = original_columns[variation_lower]
                    normalized_df[standard_name] = df[original_col]
                    break
        
        missing_columns = [col for col in self.COLUMN_MAPPINGS.keys() if col not in normalized_df.columns]
        if missing_columns:
            for col in missing_columns:
                if col == 'Stock Name' and 'SYMBOL' in df.columns:
                    normalized_df['Stock Name'] = df['SYMBOL']
                elif col == 'Stock Name' and 'ISIN' in df.columns:
                    normalized_df['Stock Name'] = df['ISIN']
        
        still_missing = [col for col in self.COLUMN_MAPPINGS.keys() if col not in normalized_df.columns]
        if still_missing:
            raise ValueError(f"Missing required columns: {', '.join(still_missing)}")
        
        return normalized_df
    
    def _convert_isin_to_symbols(self, df):
        """Convert ISIN codes to stock symbols"""
        def convert_identifier(identifier):
            if pd.isna(identifier):
                return identifier
            
            identifier = str(identifier).strip().upper()
            
            if self._is_isin(identifier):
                if identifier in self.isin_mappings:
                    return self.isin_mappings[identifier]['symbol']
                return identifier
            
            return identifier
        
        df['Stock Name'] = df['Stock Name'].apply(convert_identifier)
        return df
    
    def _is_isin(self, value):
        """Check if value looks like an ISIN code"""
        if not isinstance(value, str):
            return False
        value = value.strip()
        return bool(re.match(r'^INE[A-Z0-9]{9}$', value))
    
    def _clean_data(self, df):
        """Clean and validate data"""
        df['Buy Date'] = pd.to_datetime(df['Buy Date'], errors='coerce')
        df['Buy Price'] = pd.to_numeric(df['Buy Price'], errors='coerce')
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        
        df = df.dropna(subset=['Stock Name', 'Buy Price', 'Buy Date', 'Quantity'])
        
        df = df[df['Buy Price'] > 0]
        df = df[df['Quantity'] > 0]
        
        return df
    
    def get_unresolved_isins(self, df):
        """Get list of ISIN codes that couldn't be resolved to symbols"""
        unresolved = []
        for stock in df['Stock Name']:
            if self._is_isin(str(stock)):
                unresolved.append(stock)
        return unresolved


def parse_portfolio_file(uploaded_file):
    """Convenience function to parse portfolio files"""
    parser = PortfolioFileParser()
    return parser.parse_file(uploaded_file)
