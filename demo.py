from mftool import Mftool

# Initialize the library
mf = Mftool()

# Get a dictionary of all available mutual fund schemes
all_schemes = mf.get_scheme_codes()

# Print the first 10 schemes to see what it looks like
print("Here are 10 mutual funds available:")
for i, (code, name) in enumerate(all_schemes.items()):
    if i >= 10: break
    print(f"Code: {code} | Name: {name}")
