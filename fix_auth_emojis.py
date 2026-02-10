
path = r'c:\Users\Vedant Rao\OneDrive\Desktop\Hackathon\expense-categorisation-system-main\app.py'
with open(path, 'rb') as f:
    lines = f.readlines()

# Ensure we're targeting the right line by content if possible, but the view showed 322 (0-indexed 321)
# Checking a few lines around it to be safe
for i, line in enumerate(lines):
    if b'tab_login, tab_signup = st.tabs' in line:
        lines[i] = b'    tab_login, tab_signup = st.tabs(["\xf0\x9f\x94\x90 Login", "\xf0\x9f\x93\x9d Sign Up"])\n'
        break

with open(path, 'wb') as f:
    f.writelines(lines)
print('Auth emojis fixed.')
