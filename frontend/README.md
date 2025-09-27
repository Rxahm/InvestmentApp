# Frontend

React client for the Pretium Investment application. The app provides a simple
login flow, JWT token storage, and a screen for provisioning two-factor
authentication.

## Quick start

```bash
npm install
npm start
```

The development server runs at <http://localhost:3000>. Configure the backend
API URL via environment variable:

```bash
# .env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000/api
```

## Available scripts

- `npm start` – Start the development server.
- `npm run build` – Build for production.
- `npm test` – Run Jest tests.

The Axios instance automatically injects the JWT access token stored in
`localStorage` and logs the user out if a `401` response is returned.
