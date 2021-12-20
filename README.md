# FISHY-SPI
Description of the FISHY SPI component interface.
## Introduction
This example aims to show everything from installation to integration of tools used in SPI development. Here we will show a brief description of the steps that must be followed.
We will start by defining some basic concepts, and then describing the installation and integration of keycloak with RabbitMQ, and a client built-in Python. It is worth noting that the development is being done in Python, but in the first part of the document, we also have a small class in java, to serve as another example.
## Fundamentals
### Keycloak context
keycloak will be used as an Authorization Service (AS). It will provide authentication and authorization protocols.
#### Realm
A realm manages a set of users, their credentials, <b>roles</b>, and <b>groups</b>. A user belongs to and logs into a realm. Realms are isolated from one another and can only manage and authenticate the users that they control.
#### Client and Scopes
When a client is registered, we must define <b>protocol mappers</b> and role scope mappings for that client.
### RabbitMQ context
RabbitMQ will be used as a message broker. After <b>publishers</b> (or <b>producers</b>) are authenticated and authorized they can start sending messages to specific qeues in RabbitMQ, which will keep the data in those queues.
The information at qeues stay available for <b>consumers</b> that previously subscribed to each one. Qeues are not persistnt meaning consumers must store the data if required.
## Installing Keycloak and perform basic configuration
To install the Keycloak in a docker container, we can use the command:

```docker run -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:15.0.2```

This will start Keycloak, exposing the entry point on the local port 8080; it will also <b>create an initial admin user</b> with a <b>default password admin</b>, too.

When installing keycloak, it automatically instantiates a database. It's a good idea to create a volume so that we don't have to repeat the settings when the container shuts down.
- <b>Note</b>: Keycloak uses by default a relational DB H2 to store the authentication information, for simple test cases. This simple solution can be used without major problems. However, its replacement is highly recommended, in complex cases or production environments.

### Login to the Admin console
Using the URL: ```http://localhost:8080/auth/```, enter the **Keycloak Admin Console**, and login using the previously chosen credentials.
### Create a Realm
A realm in Keycloak is the equivalent of a tenant. By default, there is a single realm in Keycloak called <b>master</b>. This is dedicated to managing Keycloak and should not be used for other purposes. To create the first realm:
- Hover the mouse over the top-left corner where it says Master, then click on **Add realm**. 
- Fill in the form (the only obligatory field is <b>Name</b>) 
- Select Create. We have now the opportunity to add additional information (clicking on **Save**, if necessary), as shown on Figure 1.

![Figure 1 - Create a Real]()
### Create a Client
- In the top left drop-down list, select the previously created realm (Test, in the example, if it is not selected yet)
- Click <b>Clients</b> in the left side menu to open the Clients page
- On the right side, click <b>Create</b>
- We will create an **application client**. In the **Add Client** dialog box, give it an unique ID (e.g., **python_fishy**) and select the **Openid-connet** protocol. After clicking **Save** we get the client configuration page.
- On the **python_fishy client page** that appears, configure the fields as shown in Figure 2.

![Figure 2 - Client application settings]()

- **NOTE**: We must first select the **Access Type** as **confidential**. Then activate (on) the **Service Accounts Enabled** option. This parameter activates the authentication flow we intent to use in this example (**Client Credentials Flow**).
- Next we must fill in the **Valid Redirect URIs** field, whic will be the entry point for the client ```http://localhost:8081``` in our example. Don't forget to click on **Save**.
- Finally, we must select the **Credentials** tab and copy the Secret for this Client ID (python_fishy), which we will embbed in the client code next.
## Installing RabbitMQ
