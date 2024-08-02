from app import create_app, db

app = create_app()

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            print("Connected successfully")
    except Exception as e:
        print(f"Failed to connect: {e}")

    app.run(debug=True)