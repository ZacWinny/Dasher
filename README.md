# Dasher - Online Food Delivery App

Dasher is a web-based food delivery application built with Flask, a Python microframework. It allows customers to browse restaurants, order food online, and track their deliveries. Restaurant owners can manage their menus, view orders, and track revenue.

## Features

**For Customers:**

*   Browse restaurants by category, distance, and rating
*   View restaurant details and menus with images
*   Add items to cart and place orders
*   Track order status and history
*   Sign up for memberships with exclusive benefits such as discounts

**For Restaurant Owners:**

*   Manage menu items (add, edit, delete)
*   View and manage incoming orders (accept, reject, update status)
*   Generate revenue reports

## Installation and Setup

**Prerequisites:**

*   Python 3.x 
*   Pip (Python package installer)
    
**Steps:**

1.  **Navigate to the Project Directory:**

    ```bash
    cd Dasher 
    ```

    (Replace `Dasher` with the name of the directory where you have the extracted project files.)

2.  **Create and Activate a Virtual Environment:**
    *   To create an isolated environment for your project's dependencies, run the following command:
    
        ```bash
        python -m venv venv
        ```

    *   Activate the environment:

        ```bash
        # On Windows:
        venv\Scripts\activate

        # On macOS/Linux:
        source venv/bin/activate
        ```
3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up the Database:**

    ```bash
    flask db upgrade
    ```

5.  **Run the Application:**

    ```bash
    flask --app main run
    ```
    Or:
    ```bash
    python main.py
    ```

6.  **Generate Test Data (Optional):**

    ```bash
    python generate_test_data.py
    ```


7.  **Access in Your Browser:**

    Open your web browser and visit the following URL:
    
    ```
    http://127.0.0.1:5000/
    ```
    This is the local address where the Dasher app will be running.


## Technologies Used

*   **Flask:** Web framework
*   **SQLAlchemy:** ORM for database management
*   **Flask-Login:** User authentication
*   **SQLite:** Database
*   **Bootstrap:** Front-end styling
*   **Geocomplete:** Address autocomplete
*   **Faker:** For generating test data


