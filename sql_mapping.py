def sql_mapping(doctor_name):
    if doctor_name == "Терапевт":
        return "therapist"
    elif doctor_name == "Хирург":
        return "surgeon"
    elif doctor_name == "Стоматолог":
        return "dentist"
    elif doctor_name == "Пульмонолог":
        return "pulmonologist"
    return None
