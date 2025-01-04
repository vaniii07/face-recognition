#ADD Mapping of courses

COURSE_MAPPING = {
    'pharmacy': 'College of Pharmacy',
    'healthscience': 'College of Health Sciences',
    'law': 'College of Law',
    'artsandscience': 'College of Arts and Sciences',
    'criminaljustice': 'College of Criminal Justice',
    'graduateschool': 'Graduate School',
    'informationtechnology': 'College of Information Technology',
    'businessmanagement': 'College of Business Management',
    'humanscience': 'College of Human Sciences',
    'engineering': 'College of Engineering',
    'hospitality': 'College of Hospitality Management',
    'teacher': 'College of Teacher Education',
    'techvoc': 'College of Technical Vocational Education',
    'nstp': 'National Service Training Program'
}

PROGRAM_MAPPING = {
    'bsm': 'Bachelor of Science in Midwifery',
    'bsn': 'Bachelor of Science in Nursing',
    'bac': 'Bachelor of Arts in Communication',
    'edd-em': 'Doctor of Education in Educational Management',
    'maed-em': 'Master of Arts in Education major in Educational Management',
    'ma-spe': 'Master of Arts in Special Education',
    'ma-ece': 'Master of Arts in Education major in Early Childhood Education',
    'ma-nursing': 'Master of Arts in Nursing',
    'mba': 'Master in Business Administration',
    'mpa': 'Master in Public Administration',
    'bsit': 'Bachelor of Science in Information Technology',
    'blis': 'Bachelor of Library and Information Science',
    'hsncii': 'Health Care Services NC II',
    'fbsncii': 'Food and Beverage Services NC II',
    'cgncii': 'empty for now',
    'cssncii': 'Computer Systems Servicing NC II',
    'bsa': 'Bachelor of Science in Accountancy',
    'bsaba-fm': 'Bachelor of Science in Business Administration major in Financial Management',
    'bsaba-mm': 'Bachelor of Science in Business Administration major in Marketing Management',
    'bsma-mm': 'Bachelor of Science in Management Accounting',
    'bsba-hrm': 'Bachelor of Science in Business Administration major in Hotel and Restaurant Management',
    'bsoa': 'Bachelor of Science in Office Administration',
    'bssw': 'Bachelor of Science in Social Work',
    'bsce': 'Bachelor of Science in Civil Engineering',
    'bsee': 'Bachelor of Science in Electrical Engineering',
    'bsece': 'Bachelor of Science in Electronics Engineering',
    'bscpe': 'Bachelor of Science in Computer Engineering',
    'bshm': 'Bachelor of Science in Hotel Management',
    'bstm': 'Bachelor of Science in Tourism Management',
    'bsee': 'Bachelor of Secondary Education major in English',
    'bsem': 'Bachelor of Secondary Education major in Mathematics',
    'bses': 'Bachelor of Secondary Education major in Science',
    'bsef': 'Bachelor of Secondary Education major in Filipino',
    'bsess': 'Bachelor of Secondary Education major in Social Studies',
    'beedg': 'Bachelor of Elementary Education major in General Education',
    'bece': 'Bachelor of Elementary Education major in Early Childhood Education',
    'bcae': 'Bachelor of Cultural Arts Education',
    'bpe': 'Bachelor of Physical Education',
    'bsne': 'Bachelor of Science in Nutrition and Dietetics',
    'bsc': 'Bachelor of Science in Criminology'
}
    
COURSES = {
    'pharmacy': [],
    'healthscience': [{'bsm': PROGRAM_MAPPING['bsm']}, {'bsn': PROGRAM_MAPPING['bsn']}],
    'law': [],
    'artsandscience': [{'bac': PROGRAM_MAPPING['bac']}],
    'criminaljustice': [{'bsc': PROGRAM_MAPPING['bsc']}],
    'graduateschool': [{'edd-em': PROGRAM_MAPPING['edd-em']}, {'maed-em': PROGRAM_MAPPING['maed-em']}, {'ma-spe': PROGRAM_MAPPING['ma-spe']}, {'ma-ece': PROGRAM_MAPPING['ma-ece']}, {'ma-nursing': PROGRAM_MAPPING['ma-nursing']}, {'mba': PROGRAM_MAPPING['mba']}, {'mpa': PROGRAM_MAPPING['mpa']}],
    'informationtechnology': [{'bsit': PROGRAM_MAPPING['bsit']}, {'blis': PROGRAM_MAPPING['blis']}],
    'businessmanagement': [
        {'bsa': PROGRAM_MAPPING['bsa']}, 
        {'bsaba-fm': PROGRAM_MAPPING['bsaba-fm']},
        {'bsaba-mm': PROGRAM_MAPPING['bsaba-mm']},
        {'bsba-hrm': PROGRAM_MAPPING['bsba-hrm']},  # Update key to match PROGRAM_MAPPING
        {'bsoa': PROGRAM_MAPPING['bsoa']}
    ],
    'humanscience': [{'bssw': PROGRAM_MAPPING['bssw']}],
    'engineering': [{'bsce': PROGRAM_MAPPING['bsce']}, {'bsee': PROGRAM_MAPPING['bsee']}, {'bsece': PROGRAM_MAPPING['bsece']}, {'bscpe': PROGRAM_MAPPING['bscpe']}],
    'hospitality': [{'bshm': PROGRAM_MAPPING['bshm']}, {'bstm': PROGRAM_MAPPING['bstm']}],
    'teacher': [
        {'bsee': PROGRAM_MAPPING['bsee']},
        {'bsem': PROGRAM_MAPPING['bsem']},
        {'bses': PROGRAM_MAPPING['bses']},
        {'bsef': PROGRAM_MAPPING['bsef']},
        {'bsess': PROGRAM_MAPPING['bsess']},
        {'beedg': PROGRAM_MAPPING['beedg']},
        {'bece': PROGRAM_MAPPING['bece']},
        {'bcae': PROGRAM_MAPPING['bcae']},
        {'bpe': PROGRAM_MAPPING['bpe']},
        {'bsne': PROGRAM_MAPPING['bsne']}
    ],
    'techvoc': [{'hsncii': PROGRAM_MAPPING['hsncii']}, {'fbsncii': PROGRAM_MAPPING['fbsncii']}, {'cgncii': PROGRAM_MAPPING['cgncii']}, {'cssncii': PROGRAM_MAPPING['cssncii']}],
    'nstp': []
}