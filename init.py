from src.cute import init_db
print('Regenerating CuteCasa DB...')
init_db()
print('Done.')



yn = input('Create admin user? [y/N] ')
if yn not in ['Y', 'y', 'yes', 'Yes']:
    exit(0)

adminName = input('Admin user name: ')
adminPass =input('Admin user password: ')

# TODO: Refactor things into routes vs. core, and have registration functionality (among other things) in core
print('Todo...')