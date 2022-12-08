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

def from_sql_mapping(sql_doctor_name):
    if sql_doctor_name == "therapist":
        return "Терапевт"
    elif sql_doctor_name == "surgeon":
        return "Хирург"
    elif sql_doctor_name == "dentist":
        return "Стоматолог"
    elif sql_doctor_name == "pulmonologyst":
        return "Пульмонолог"
    return None
