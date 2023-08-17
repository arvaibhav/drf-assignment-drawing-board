# Drawing Board Assignment

## Project Setup
### Running with Docker

1. Clone the project repository.
2. Navigate to the project directory.
3. Build the Docker image: `docker build -t drawing_board .`
4. Run the Docker container: `docker run -p 8000:8000 drawing_board`
5. The API will be accessible at `http://127.0.0.1:8000/`.

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

* PUBLIC_READ: Anyone can read the drawing board.
* PROTECTED_READ: Only authenticated users can read the drawing board.
* PROTECTED_READ_WRITE: Only authenticated users can read and modify the drawing board.
* USER_READ: Only the owner and users shared with can read the drawing board.
* USER_READ_WRITE: Only the owner and users shared with can read and modify the drawing board.


___

# Drawing Session Process Flow
The DrawingSession model defines how a user can perform actions on a drawing board, capturing and storing the details of each action. Below is the working flow for handling drawing sessions:
 
---

### WebSocket Functionality (Planned)

In the future, WebSocket functionality will be added to enable real-time collaboration on drawing sessions. Here are the checks and features that will be implemented:

1. **User Start Session:** When a user begins drawing, the client will send a "start session" request along with the necessary meta-data to initiate the drawing session. If the user is not authenticated or does not have the right permissions, an error will be returned.

2. **User End Session:** When a user completes drawing, the client will send an "end session" request along with the respective meta-data to conclude the drawing session. If the user is not authenticated or does not have the right permissions, an error will be returned.

3. **Interactions During Ongoing Session:** If another user attempts to interact with a drawing session that is already ongoing, an error will be returned, indicating that an action is in progress by another user. This ensures that only one user can perform actions on a drawing session at a time.

4. **Unauthorized User Interactions:** If a user tries to interact with a drawing session but is not authenticated or does not have the appropriate permissions, an error will be returned. This ensures that only authorized users can perform actions on a drawing board.

5. **Undo/Redo Version System:** A versioning system will be implemented to allow users to undo and redo actions within a drawing session. Each action will be assigned a version number, and users will be able to navigate through versions to achieve undo/redo functionality.


####    Performing Actions:
The user can perform various actions, defined in core/constants.py within the ActionTypeEnum class. These actions include:

  -   Freehand drawing (FREEHAND_DRAW)
  - Drawing lines (DRAW_LINE)
  - Drawing polygons (DRAW_POLYGON)
  - Writing text (WRITE_TEXT)
---
