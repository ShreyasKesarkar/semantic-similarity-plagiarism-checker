def get_risk(similarity):
    if similarity < 30:
        return "LOW"
    elif similarity < 60:
        return "MEDIUM"
    elif similarity < 80:
        return "HIGH"
    else:
        return "VERY HIGH"