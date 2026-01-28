import math

def calculate_wheel_speeds(speed, angle_deg, angular_velocity, angular_speed_ratio=-1.0):
    """
    Calculates motor speeds for a 4-wheel omni-directional robot (Bozotics Style).
    
    Args:
        speed (float): Linear speed magnitude (0-100 or 0-1000).
        angle_deg (float): Direction of movement in degrees (0-360).
        angular_velocity (float): Rotational correction factor (e.g. from PID).
        angular_speed_ratio (float): Optional override for rotation speed scaling. 
                                     If -1.0, uses 'speed'.
    
    Returns:
        tuple: (fl, fr, bl, br) motor speeds.
    """
    
    if angular_speed_ratio == -1.0:
        angular_speed_ratio = speed

    # Convert to radians
    # Note: Bozotics uses a specific offset or coord system. 
    # Standard Omni: 
    # FL = sin(a+45)
    # Bozotics Implementation:
    # x_co = sin(rad)*0.707
    # y_co = cos(rad)*0.707
    # fl = (x+y)*speed + ...
    
    rad_ang = math.radians(angle_deg)
    
    # 0.707 is approx 1/sqrt(2), normalizing the 45 degree mounting
    x_co = math.sin(rad_ang) * 0.707
    y_co = math.cos(rad_ang) * 0.707
    
    # Mixing linear vector with angular rotation
    # Assuming standard X configuration
    fl = (x_co + y_co) * speed + (0.1 * angular_velocity) * angular_speed_ratio
    bl = (-x_co + y_co) * speed + (0.1 * angular_velocity) * angular_speed_ratio
    fr = (-x_co + y_co) * speed - (0.1 * angular_velocity) * angular_speed_ratio
    br = (x_co + y_co) * speed - (0.1 * angular_velocity) * angular_speed_ratio
    
    return fl, fr, bl, br

def normalize_speeds(fl, fr, bl, br, max_val=100.0):
    """
    Normalizes wheel speeds to fit within a maximum range (-max_val to +max_val)
    preserves ratio if limit exceeded.
    """
    max_speed = max(abs(fl), abs(fr), abs(bl), abs(br))
    
    if max_speed > max_val:
        scale = max_val / max_speed
        fl *= scale
        fr *= scale
        bl *= scale
        br *= scale
        
    return fl, fr, bl, br
