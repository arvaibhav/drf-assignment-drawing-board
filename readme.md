# Drawing Board Assignment

## Project Setup
### Running with Docker

1. Clone the project repository.
2. Navigate to the project directory.
3. Build the Docker image: `docker build -t drawing_board .`
4. Run the Docker container: `docker run -p 8000:8000 drawing_board`
5. The API will be accessible at `http://127.0.0.1:8000/`.

# Project Structure

## Configuration

- `config_manager`: Handles various configurations such as development and production settings.
  - `/base.py`: Base configuration file.
  - `/development.py`: Development-specific settings.
  - `/production.py`: Production-specific settings.

## Core Logic

- `core`: Contains core functionalities and constants.
  - `/concurrent_drawing_control.py`: Manages concurrent drawing controls.
  - `/constants.py`: Defines constant values used across the project.
  - `/drawing_board_session.py`: Handles drawing board sessions.
  - `/drawing_board_user_permission.py`: Manages user permissions for drawing boards.

## Database

- `db`: Database-related files including migrations and models.
  - `/models`: Database model definitions.

## Endpoints

- `endpoints`: Defines API endpoints, middleware, and websockets.
  - `/api`: API definitions, serializers, and tests.
  - `/middleware`: Middleware for authentication and error logging.
  - `/websockets`: Websocket-related files.

## Utilities

- `utils`: General utility functions and classes.
  - `/distributed_lock.py`: A utility for distributed locking mechanism. (Interface)

## API Overview

The Drawing Board API allows users to manage drawing boards, including creating, sharing, viewing, and listing drawing boards. Here's a high-level flow description:
also added in postman collection
1. **User Signup:** Allows new users to register an account.
2. **User Login:** Allows existing users to authenticate.
3. **Create Drawing Board:** Authenticated users can create new drawing boards.
4. **View Drawing Board:** Users can view drawing board details based on permission.
5. **Share Drawing Board:** Authenticated owners can share drawing boards with other users.
6. **List Drawing Boards:** Authenticated users can list drawing boards they own or are shared with.


### User Signup

- **URL:** `/users/signup/`
- **Method:** `POST`

### User Login

- **URL:** `/users/login/`
- **Method:** `POST`

### Create Drawing Board

- **URL:** `/drawing_boards/`
- **Method:** `POST`
- **Headers:** `USERID: user_id, Content-Type: application/json`

### View Drawing Board

- **URL:** `/drawing_boards/(?P<unique_id>[0-9a-f-]+)/`
- **Method:** `GET`
- **Headers:** `USERID: user_id, Content-Type: application/json` (based on permission)

### Share Drawing Board (or alternative name for this view)

- **URL:** `/drawing_boards/(?P<unique_id>[0-9a-f-]+)/share/`
- **Method:** `POST`
- **Headers:** `USERID: user_id, Content-Type: application/json`

### List Drawing Boards

- **URL:** `/drawing_boards/list/`
- **Method:** `GET`
- **Headers:** `USERID: user_id, Content-Type: application/json`


#   Project Flow Description
##  User Signup: 
Users can sign up by sending a POST request to /api/v1/signup/ with their username and password. The server will create a new user and return a token for authentication.

##  User Login:
Users can log in by sending a POST request to /api/v1/login/ with their username and password. The server will authenticate the user and return a token for further requests.

## Create Drawing Board:
Authenticated users can create a new drawing board by sending a POST request to /api/v1/drawing_boards/create/. They need to provide the permission type and the list of shared users (if applicable). The server will create the drawing board and associated shared permissions.

## View Drawing Board Detail:
Users can view the details of a specific drawing board by sending a GET request to /api/v1/drawing_boards/<unique_id>/. The server will provide information about the drawing board's permission type and shared users.

## View Drawing Board List:
Users can view their owned drawing boards and boards shared with them by sending a GET request to /api/v1/drawing_boards/. The server will return a list of drawing boards with their details.

## Drawing Board Sharing:
Users can update the sharing permissions of a drawing board by sending a POST request to /api/v1/drawing_boards/share/. They need to provide the drawing board's unique_id, the permission type, and the list of shared users (if applicable). The server will update the sharing permissions accordingly.

# Permissions
#####  In the core/constants.py file, there are defined constants for different permission types:

* `PUBLIC_READ` (1): Anyone can read the drawing board.
* `USER_READ` (2): Only the owner and users shared with can read the drawing board.
* `USER_WRITE` (4): Only the owner and users shared with can modify the drawing board.
* `PROTECTED_READ` (8): Not specific to a particular user, but any registered user can read the drawing board.
* `PROTECTED_WRITE` (16): Not specific to a particular user, but any registered user can modify the drawing board.

There are also combination permissions:

* `USER_WRITE_PUBLIC_READ` (5): Combination of `USER_WRITE` and `PUBLIC_READ`.
* `PROTECTED_WRITE_PUBLIC_READ` (17): Combination of `PROTECTED_WRITE` and `PUBLIC_READ`.
* `USER_WRITE_PROTECTED_READ` (12): Combination of `USER_WRITE` and `PROTECTED_READ`.


# Drawing Board WebSocket Consumer
## 1. connect method

- **Purpose**: Establishes a WebSocket connection between the client and server.
- **Process**:
  - Parses the query string to extract the drawing board ID and user ID.
  - Retrieves the permissions for the current user on the given drawing board.
  - Adds the connection to the group if the user has read permission and accepts the WebSocket connection.
  - Closes the connection with a specific code if the user doesn't have read permission.

## 2. disconnect method

- **Purpose**: Handles the closure of a WebSocket connection.
- **Process**:
  - Closes all drawing sessions associated with the current user and drawing board.
  - Removes the connection from the group.
  - If the user evokes particular user permission, we disconnect their connection (ref: `core.drawing_board_user_permission.remove_users_from_drawing_board_and_socket_channel`).

## 3. receive_json method

- **Purpose**: Handles incoming JSON messages over the WebSocket.
- **Process**:
  - Client uses this to start and end drawing sessions:
  - Start drawing session flow:
    - Extracts action and metadata for drawing operation.
    - Calls `do_drawing_operation_sessions` to perform the drawing operation.
    - Sends an error message if a `DrawingOperationException` is caught.
    - **Performing Actions**: The user can perform various actions, defined in `core/constants.py` within the ActionTypeEnum class. These actions include:
        - Freehand drawing (FREEHAND_DRAW)
        - Drawing lines (DRAW_LINE)
        - Drawing polygons (DRAW_POLYGON)
        - Writing text (WRITE_TEXT)
        - UNDO
        - REDO
  - End drawing session:
    - Sends a response to all group members using broadcast if successful during the end of the drawing session.

## For Concurrency Management -> Use of Lock

- **Initial Implementation**: Uses an in-memory lock.
- **Alternative**: Planned to be replaced by a distributed lock using Redis for more robust concurrent control across multiple servers.
- **Usage in Code**:
  - Acquires a lock based on the drawing board ID in `do_drawing_operation_sessions`.
  - Raises a `DrawingOperationException` if the lock cannot be acquired.
  - Releases the lock after the operation, allowing others to proceed.
- **Note**: The lock mechanism ensures that these operations occur in a sequential manner for each drawing board, preventing conflicting or concurrent modifications.
  - Indeed: If a drawing session is started by user X, then all have to wait till X's drawing session is not closed; `do_drawing_operation_sessions` can throw an error based on concurrent lock or if drawing action is being performed by another user and not closed yet (DB query based check wherein models' `ended_at` field is updated when the session ends).
# Other Enhancement
# Authentication Using Encrypted JWT with Refresh Mechanism
- **Reduced Query Costs**: By storing user information in the token, the system avoids additional queries to fetch user data.
- **Flexibility**: Supports both REST and WebSocket connections and can implement on different lang. backend (compared to cookies which are not supportable)

## Middleware for JWT Authentication

### HTTP Token Middleware

The `HttpTokenMiddleware` class is responsible for extracting and validating the JWT from the HTTP header in the REST API requests. Upon successful validation, it adds the payload to the request object. In case of any error, it returns a 401 Unauthorized response.

### WebSocket Token Middleware

The `WebsocketTokenMiddleware` class handles WebSocket connections. It extracts the token from the WebSocket header and validates it. If the token is valid, the payload is added to the scope object, and the connection is allowed. If there's an error in validation, the connection is denied.

## User Authentication Views

### User Signup View

The `UserSignupView` is a create API view that handles user registration. After successful registration, it returns access and refresh tokens.

### User Login View

The `UserLoginView` handles user login and, upon successful authentication, returns access and refresh tokens. The `generate_user_token` function is used to create these tokens.

### Refresh Token View

The `RefreshTokenView` allows the user to refresh the access token using the refresh token. This ensures that the user can continue to authenticate without having to log in again when the access token expires.

## Token Generation and Validation Functions

- **generate_user_token**: Generates access and refresh tokens for the given user ID.
- **create_access_token**: Creates an access token using the user information.
- **create_refresh_token**: Creates a refresh token that can be used to obtain a new access token.
- **validate_access_token**: Validates the token to ensure its integrity and authenticity.


- **Refresh Token**: Alongside the JWT, a refresh token is issued at login.
- **Expiration Handling**: When the JWT expires, the refresh token can be used to obtain a new JWT.
- **Security Measures**: Refresh tokens are stored securely and can be revoked if needed.



---
