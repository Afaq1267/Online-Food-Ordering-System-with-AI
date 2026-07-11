from app import app, db

print("=" * 50)
print("⚠️  WARNING: This will DELETE ALL DATA!")
print("=" * 50)

confirm = input("Type 'YES' to confirm: ")

if confirm == "YES":
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully!")
        print("✅ All tables recreated!")
else:
    print("❌ Cancelled. No changes made.")