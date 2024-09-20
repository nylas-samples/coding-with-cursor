# Coding with Cursor 

This repository contains the code for getting started Coding with Cursor. 

The application is detailed below and includes both a backend (`/backend`) and frontend (`/frontend`) applications that need to be started separately and each folder consists of a `README.md` on how to run the application.

<img width="1203" alt="Screenshot 2024-09-20 at 3 44 32 PM" src="https://github.com/user-attachments/assets/423a38e2-354c-41f2-988f-16b0bd3699b1">

## Application Overview:

### Web Email Client: Read and Send Emails using Nylas Email API

- [ ] Insert Application Image

The application is a web email client that allows users to read and send emails using the Nylas Email API. It is built with a React frontend and a Node.js backend. Once a user authenticates, it allows them to interact with the Nylas APIs from a web client.

#### Prerequisites

Before you get started, sign up for an account on [Nylas](https://nylas.com) if you don't already have one.
- [ ] Insert UTM link to Nylas and test

Use the Nylas Dashboard to create an application and grab a copy of your `client id` and click on `API Keys` to create and an API Key. You'll need those later on to build the application.

#### ⚙️ Environment Setup

Let’s check that our environment is set up to use the [Nylas Node SDK](https://github.com/nylas/nylas-nodejs). Check the Node version in your terminal:

```bash
$ node -v
v18.0.0
```

If you don’t see a version returned, you may not have Node installed. Try the following steps:

1. Visit [nodejs.org](https://nodejs.org/en/) to set up Node on your machine
2. _Recommended_: If you happen to use or require multiple versions of Node, consider using [nvm](https://github.com/nvm-sh/nvm)

The minimum required Node version is `v18.0.0`. As a quick check, try running `node -v` again to confirm the version. You may need to restart your terminal for the changes to take effect.

#### ⚡️ App Set up

View the `README.md` files in the `backend` and `frontend` directories for instructions on how to set up the server and client. These README files include set up instructions for each language.

Start the backend server first, then in a new terminal, start the frontend server.

Once the servers are running, visit the app at [http://localhost:3000](http://localhost:3000). You can also visit the backend server at [http://localhost:9000](http://localhost:9000).

#### 💙 Contributing

Interested in contributing to the Nylas use cases project? Thanks so much for your interest! We are always looking for improvements to the project and contributions from open-source developers are greatly appreciated.

Please refer to [Contributing](CONTRIBUTING.md) for information about how to make contributions to this project. We welcome questions, bug reports, and pull requests.

#### 📝 License

This project is licensed under the terms of the MIT license. Please refer to [LICENSE](LICENSE.txt) for the full terms.
