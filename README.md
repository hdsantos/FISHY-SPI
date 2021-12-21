# FISHY-SPI
Description of the FISHY SPI component interface.
## Introduction
This example shows the details from installation to integration of tools used in SPI development. Here we will conduct a brief description of the steps that we must follow to have a basic deployment of the module.
We will start by defining some basic concepts and then describing the installation and integration of keycloak with RabbitMQ, and a template client, written both in Python and Java.
## Fundamentals
### Keycloak context
Keycloak will be used as an Authorization Service (AS). It will provide authentication and authorization protocols. As an implementation of the OpenID and OAuth2 protocols, Keycloak supports user authentication, locally or in a federation, and application authentication. In this case, we are mainly interested in this last aspect, namely the so-called [Client Credential Flow](https://auth0.com/docs/authorization/flows/client-credentials-flow).
#### Realm
A realm manages a set of users, their credentials, **roles**, and **groups**. A user belongs to and logs into a realm. Realms are isolated and obviously can only manage and authenticate users under their control.
#### Client and Scopes
When a client is registered, we must define its **protocol mappers** and **role scope** mappings.
### RabbitMQ context
RabbitMQ will be used as a message broker. After **publishers** (or **producers**) are authenticated and authorized, they can start sending messages to specific queues in RabbitMQ, which will keep the data in those queues. The information at queues stays available for **consumers** that previously subscribed to each one. <u>Qeues are not persistent</u> meaning consumers must store the data if required.
## Installing Keycloak and perform basic configuration
To install the Keycloak in a docker container, we can use the command:

```docker run -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:15.0.2```

This will start Keycloak, exposing the entry point on the local port 8080; it will also <b>create an initial admin user</b> with a <b>default password admin</b>, too.

When installing keycloak, it automatically instantiates a database. It's a good idea to create a volume so that we don't have to repeat the settings when the container shuts down.
- **Note**: Keycloak uses by default a relational DB H2 to store the authentication information, for simple test cases. This simple solution can be used without major problems. However, its replacement is highly recommended, in complex cases or production environments.

### Login to the Admin console
Using the URL: ```http://localhost:8080/auth/```, enter the **Keycloak Admin Console**, and login using the previously chosen credentials.
### Create a Realm
A realm in Keycloak is the equivalent of a tenant. By default, there is a single realm in Keycloak called <b>master</b>. This is dedicated to managing Keycloak and should not be used for other purposes. To create the first realm:
- Hover the mouse over the top-left corner where it says Master, then click on **Add realm**. 
- Fill in the form (the only mandatory field is **Name**) 
- Select **Create**, and we will get the **General** page for the Test realm, as shown in Figure 1, and where we can add additional information (do not forget to click on **Save**, if necessary).

![Figure 1 - Create a Realm](images/Figure1.png)

### Create a Client
In the example that follows we will create an application client that will use a dedicated control flow which do not require any authentication from the user (within FISHY this will be the most frequent case).
- In the top left drop-down list, select the previously created realm (Test, in the example, if it is not selected yet)
- Click <b>Clients</b> in the left side menu to open the Clients page
- On the right side, click <b>Create</b>
- We will create an **application client**. In the **Add Client** dialog box, give it an unique ID (e.g., **python_fishy**) and select the **Openid-connet** protocol. After clicking **Save** we get the client configuration page.
- On the **python_fishy client page** that appears, configure the fields as shown in Figure 2.

![Figure 2 - Client application settings](images/Figure2.png)

- **NOTE**: We must first select the **Access Type** as **confidential**. Then activate (on) the **Service Accounts Enabled** option. This parameter activates the authentication flow we intent to use in this example (**Client Credentials Flow**).
- Next we must fill in the **Valid Redirect URIs** field, whic will be the entry point for the client ```http://localhost:8081``` in our example. Don't forget to click on **Save**.
- Finally, we must select the **Credentials** tab and copy the **Secret** for this Client ID (python_fishy), which we will embbed in the client code next.

### Testing and templates (Python and Java)
For illustration and testing purposes we developed two templates with the code required to interface Keycloak, both in Python and Java. For the Java example we also created a different client using the same procedure described above.

For authentication, it is necessary to pass the parameters **Client ID**, **Client Secret** (obtained previously), and **Scope** (with an optional scope value, email in the examples, but it cloud be anything else). The call must be made to the proper **token endpoint**. The “grant type” specifies the flow to use – in the next example, ‘client_credentials’ denotes **CCF** (**Client Credential Flow**).

[Example in Python](FISHY-ccflow-ex.py)

[Example in Java](FISHY-ccflow-ex.java)

## Installing RabbitMQ
To install the RabbitMQ in a container, we can use the command:

```docker run -d --hostname rabbit-test --name rabbitmq-simulator -p 8082:15672 -p 5672:5672 rabbitmq:3-management```

In the above command, port 5672 is used for RabbitMQ client connections and port 8082 is for the RabbitMQ management page.

### Accessing RabbitMQ

We can access the RabbitMQ main page using the URL ```http://localhost:8081```, and using the default username and password, **guest**. Figure 3 shows the main page, from where we can monitor the activity, as weel as performing some configurations, like creating quees and logins management (as usual, it is recommenden to modify the default administration login).
- **Note**: concerning queues creation it is not necessary to perform it from the management site, since producers can also make it when sending data.

![Figure 3 - RabbitMQ admin console](images/Figure3.png)
