# Inside the loop in upload_students.py
for index, row in df.iterrows():
    full_name = str(row['username']).strip() # "Priya Rajeshbhai Chauhan"
    
    # We use the enrollment number as the actual 'username' for logging in 
    # because it is unique and has no spaces.
    # We save the Full Name in the first_name field.
    
    enrollment = str(row['enrollment_number']).split('.')[0]
    
    if not User.objects.filter(username=enrollment).exists():
        user = User.objects.create_user(
            username=enrollment,  # Use enrollment for login
            first_name=full_name, # Save Full Name here
            email=row['email'],
            password=str(row['password']),
            enrollment_number=enrollment,
            branch=row['branch'],
            semester=row['semester'],
            is_student=True
        )
        StudentData.objects.create(student=user)
        print(f"Created: {full_name} with ID {enrollment}")
