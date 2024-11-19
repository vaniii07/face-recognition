import bcrypt

# The hashed password from Laravel
hashed_password = b'$2b$12$MNdYSyPOpAtWAqIEYRc1y.CYc0bDcJkXIEeVbM39D7Spp.ev.j.oC'  # Example hash

# The plain text password to check
password = '12345678'

# Verify if the password matches the hash
if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
    print("Password match!")
else:
    print("Password does not match.")