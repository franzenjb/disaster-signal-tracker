import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DisasterRiskEngine:
    """Advanced risk assessment and scoring for disaster events"""
    
    SEVERITY_WEIGHTS = {
        'Minor': 1,
        'Moderate': 2, 
        'Severe': 4,
        'Extreme': 8
    }
    
    EVENT_MULTIPLIERS = {
        'Earthquake': {'base': 3, 'magnitude_factor': 2},
        'Wildfire': {'base': 2, 'confidence_factor': 1.5},
        'Flood Warning': {'base': 4, 'duration_factor': 1.2},
        'Flood Advisory': {'base': 2, 'duration_factor': 1.1},
        'Hurricane': {'base': 8, 'category_factor': 2},
        'Tornado': {'base': 6, 'ef_factor': 3}
    }
    
    @staticmethod
    def calculate_earthquake_risk(row):
        """Calculate earthquake risk based on magnitude and depth"""
        mag = row.get('magnitude', 0)
        if mag < 3.0:
            return 'LOW'
        elif mag < 5.0:
            return 'MODERATE'
        elif mag < 6.5:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    @staticmethod
    def calculate_wildfire_risk(row):
        """Calculate wildfire risk based on confidence and brightness"""
        confidence = row.get('confidence', 0)
        brightness = row.get('brightness', 0)
        
        risk_score = (confidence / 100) * (brightness / 400)
        
        if risk_score < 0.3:
            return 'LOW'
        elif risk_score < 0.6:
            return 'MODERATE'
        elif risk_score < 0.8:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    @staticmethod
    def calculate_weather_risk(row):
        """Calculate weather event risk based on severity"""
        severity = row.get('severity', 'Minor')
        if severity in ['Extreme', 'Severe']:
            return 'HIGH'
        elif severity == 'Moderate':
            return 'MODERATE'
        else:
            return 'LOW'
    
    @classmethod
    def assess_risk_level(cls, row):
        """Main risk assessment function"""
        event_type = row.get('event', '').lower()
        source = row.get('source', '')
        
        if source == 'USGS':
            return cls.calculate_earthquake_risk(row)
        elif source == 'NASA-FIRMS':
            return cls.calculate_wildfire_risk(row)
        elif source == 'NOAA':
            return cls.calculate_weather_risk(row)
        else:
            return 'UNKNOWN'
    
    @staticmethod
    def get_impact_radius(row):
        """Estimate impact radius in kilometers"""
        source = row.get('source', '')
        event = row.get('event', '')
        
        if source == 'USGS':
            mag = row.get('magnitude', 0)
            return max(10, mag * 50)  # 50km per magnitude unit
        elif source == 'NASA-FIRMS':
            confidence = row.get('confidence', 50)
            return max(5, confidence / 10)  # 5-10km radius
        elif source == 'NOAA':
            if 'flood' in event.lower():
                return 25  # 25km flood impact
            else:
                return 50  # general weather impact
        return 10
    
    @classmethod
    def enrich_disaster_data(cls, df):
        """Add risk scores and impact data to disaster dataset"""
        df = df.copy()
        
        # Add risk assessments
        df['risk_level'] = df.apply(cls.assess_risk_level, axis=1)
        df['impact_radius_km'] = df.apply(cls.get_impact_radius, axis=1)
        
        # Add time-based urgency
        now = datetime.now()
        for time_col in ['time', 'acq_datetime']:
            if time_col in df.columns:
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
                df['hours_ago'] = (now - df[time_col]).dt.total_seconds() / 3600
                df['urgency'] = df['hours_ago'].apply(lambda x: 'IMMEDIATE' if x < 1 else 
                                                    'HIGH' if x < 6 else 
                                                    'MEDIUM' if x < 24 else 'LOW')
                break
        
        # Calculate composite threat score (0-100)
        risk_scores = {'LOW': 10, 'MODERATE': 30, 'HIGH': 70, 'EXTREME': 100}
        urgency_scores = {'IMMEDIATE': 40, 'HIGH': 30, 'MEDIUM': 20, 'LOW': 10}
        
        df['risk_score'] = df['risk_level'].map(risk_scores).fillna(10)
        df['urgency_score'] = df.get('urgency', 'LOW').map(urgency_scores).fillna(10)
        df['threat_score'] = (df['risk_score'] * 0.7 + df['urgency_score'] * 0.3).round(1)
        
        return df

if __name__ == "__main__":
    # Test the risk engine
    df = pd.read_csv("combined_disaster_feed.csv")
    enriched = DisasterRiskEngine.enrich_disaster_data(df)
    
    print("🎯 Risk Assessment Summary:")
    print(enriched['risk_level'].value_counts())
    print("\n⚡ Top 10 Highest Threat Events:")
    top_threats = enriched.nlargest(10, 'threat_score')[['source', 'event', 'area', 'place', 'risk_level', 'threat_score']]
    print(top_threats.to_string(index=False))
    
    enriched.to_csv("enriched_disaster_feed.csv", index=False)
    print(f"\n✅ Enriched dataset saved with {len(enriched)} events")