from datetime import datetime

class Reading:
    """Model class for blood pressure readings."""
    
    def __init__(self, systolic, diastolic, heart_rate=None, 
                reading_datetime=None, description=None, id=None, user_id=None):
        self.id = id
        self.user_id = user_id
        self.systolic = systolic
        self.diastolic = diastolic
        self.heart_rate = heart_rate
        self.reading_datetime = reading_datetime or datetime.now().replace(second=0, microsecond=0)
        self.description = description
    
    @classmethod
    def from_tuple(cls, data_tuple):
        """Create a Reading object from a database tuple."""
        # Expected tuple format: (systolic, diastolic, heart_rate, reading_datetime, description)
        return cls(
            systolic=data_tuple[0],
            diastolic=data_tuple[1],
            heart_rate=data_tuple[2],
            reading_datetime=datetime.strptime(data_tuple[3], "%Y-%m-%d %H:%M:%S"),
            description=data_tuple[4]
        )
    
    @property
    def is_normal(self):
        """Check if the reading is within normal range."""
        return (self.systolic < 120 and self.diastolic < 80)
    
    @property
    def is_elevated(self):
        """Check if the reading indicates elevated blood pressure."""
        return (120 <= self.systolic <= 129 and self.diastolic < 80)
    
    @property
    def is_stage1(self):
        """Check if the reading indicates stage 1 hypertension."""
        return (130 <= self.systolic <= 139 or 80 <= self.diastolic <= 89)
    
    @property
    def is_stage2(self):
        """Check if the reading indicates stage 2 hypertension."""
        return (self.systolic >= 140 or self.diastolic >= 90)
    
    @property
    def is_crisis(self):
        """Check if the reading indicates hypertensive crisis."""
        return (self.systolic > 180 or self.diastolic > 120)
    
    def __str__(self):
        """String representation of the reading."""
        time_str = self.reading_datetime.strftime('%H:%M')
        heart_str = f", Heart Rate: {self.heart_rate}" if self.heart_rate else ""
        desc_str = f", Description: {self.description}" if self.description else ""
        return f"{time_str} - Systolic: {self.systolic}, Diastolic: {self.diastolic}{heart_str}{desc_str}"