#!/bin/bash

# Install PostgreSQL using Homebrew
echo "Installing PostgreSQL with Homebrew..."
brew install postgresql

# Start PostgreSQL service
brew services start postgresql


# Add dependencies
echo "Adding project dependencies..."
poetry add sqlmodel psycopg2-binary openai

# Create SQLModel and OpenAI script files (Modify these files as per your model and database requirements)
# Assume `models.py` and `seed_data.py` are provided here with appropriate content
echo "Creating model and seed data scripts..."
cat > models.py << EOF
# models.py content goes here
EOF

cat > seed_data.py << EOF
# seed_data.py content goes here
EOF

# Navigate back to the main project directory
cd ..

# Run the Python seed script to populate the database
echo "Populating the database with seed data..."
poetry run python project/seed_data.py

# Run a vector search query (replace this with your actual query script)
echo "Running a vector search query..."
poetry run python project/vector_search.py

echo "Setup complete! Vector search result has been printed."
