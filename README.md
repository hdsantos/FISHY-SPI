# FISHY-SPI
Description of the FISHY SPI component interface.
## Introduction
This example shows the details from installation to integration of the tools used in SPI development. Here we will briefly describe the steps that we must follow to have a basic deployment of the module.
We'll start by defining some basic concepts and then describing the installation and integration of the keycloak, Kong(API Gateway) with RabbitMQ and a template client, written in Python and Java. To facilitate testing and visualization of the information, we will use a GUI called Konga, an open-source tool, developed by the community, attention that this tool will be used for testing purposes. We end with a brief description of the framework developed to test the module, including a prototype producer and consumer, both written in Python.
## Fundamentals
### Keycloak context
[Keycloak](https://www.keycloak.org/) will be used as an Authorization Service (AS). It will provide authentication and authorization protocols. As an implementation of the OpenID and OAuth2 protocols, Keycloak supports user authentication, locally or in a federation, and application authentication. In this case, we are mainly interested in this last aspect, namely the so-called [Client Credential Flow](https://auth0.com/docs/authorization/flows/client-credentials-flow).
#### Realm
A realm manages a set of users, their credentials, **roles**, and **groups**. A user belongs to and logs into a realm. Realms are isolated and obviously can only manage and authenticate users under their control.
#### Client and Scopes
When a client is registered, we must define its **protocol mappers** and **role scope** mappings.
### Kong API Gateway
[Kong](https://konghq.com/) An API gateway acts as a reverse proxy to accept all application programming interface (API) calls, aggregate the various services needed to service them and return the appropriate result. In our case, it will be used to manage all calls and integrated with keycloak, to perform token validations and direct calls to their respective endpoints.
### Konga GUI
[Konga](https://pantsel.github.io/konga/) It is only used to facilitate testing and visualization of configurations that are running on kong. Attention, using this tool is for testing purposes.
### RabbitMQ context
[RabbitMQ](https://www.rabbitmq.com/) will be used as a message broker. After **publishers** (or **producers**) are authenticated and authorized, they can start sending messages to specific queues in RabbitMQ, which will keep the data in those queues. The information at queues stays available for **consumers** that previously subscribed to each one. <u>Qeues are not persistent</u> meaning consumers must store the data if required.
## Installation
## Docker
Make sure you have docker installed.

## clone the repository
```$git clone https://github.com/hdsantos/FISHY-SPI.git```

## Starting the containers

*```$$cd FISHY-SPI```
*```$docker-compose up -d keycloak-db kong-db```
*```$docker-compose run --rm kong kong migrations bootstrap```
*```$docker-compose up -d```

To install the Keycloak in a docker container, we can use the command:

```docker run -d -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:16.1.0```

This will start Keycloak as a normal process (not as a daemon), exposing the entry point on the local port 8080; it will also **create an initial admin user** with a **default password admin**.
> **Note**: executing it as a process is a good idea in the testing phase for debugging purposes since we can see all system output in the process shell window. However, it will be better to run it as a daemon in production.

When installing Keycloak, it automatically instantiates a database. It's a good idea to create a volume so that we don't have to repeat the settings when the container shuts down.
> **Note**: Keycloak uses by default a relational H2 Database Engine to store the authentication information. We can use this simple solution without significant problems. However, in production and more complex environments, replacing it with a more robust DB and **using a persistent volume** is highly recommended.

### Login to the Admin console
Using the URL: ```http://localhost:8080/auth/```, enter the **Keycloak Admin Console**, and log in using the previously chosen credentials.
### Create a Realm
A realm in Keycloak is the equivalent of a tenant. There is a single realm in Keycloak called **master** by default. That is dedicated to managing Keycloak and should not be used for other purposes. To create the first realm:
- Hover the mouse over the top-left corner where it says Master, then click on **Add realm**. 
- Fill in the form (the only mandatory field is **Name**) 
- Select **Create**, and we will get the **General** page for the Test realm, as shown in Figure 1, and where we can add additional information (do not forget to click on **Save**, if necessary).

![Figure 1 - Create a Realm](images/Figure1.png)

### Create a Client
In the example that follows, we will create an application client that will use a dedicated control flow that does not require any authentication from the user (within FISHY, this will be the most frequent case).
- In the top-left drop-down list, select the previously created realm (Test, in the example, if it is not selected yet).
- Click **Clients** in the left side menu to open the Clients page.
- On the right-side, click **Create**.
- We will create an **application client**. In the **Add Client** dialog box, give it an unique ID (e.g., **python_fishy**) and select the **OpenID-connect** protocol. After clicking **Save** we get the client configuration page.
- On the **python_fishy client page** that appears, configure the fields as shown in Figure 2.

![Figure 2 - Client application settings](images/Figure2.png)

- **NOTE**: We must first select the **Access Type** as **confidential**. Then activate (on) the **Service Accounts Enabled** option. This parameter activates the authentication flow we intent to use in this example (**Client Credentials Flow**, as already mentioned).
- Next, we must fill in the **Valid Redirect URIs** field, which will be the entry point for client redirections (```http://localhost:8081``` in our example), even if we do not use it, like in our example. Similarly, just for completeness reasons, we will be filling the Root URL (```http://localhost:8080```).  Don't forget to click on **Save**.
- Finally, we must select the **Credentials** tab and copy the **Secret** for this Client ID (python_fishy), which we will embed in the client code next.

### Testing and templates (Python and Java)
We developed two templates with the code required to interface with Keycloak, both in Python and Java, for illustration and testing purposes.

For authentication, it is necessary to pass the parameters **Client ID**, **Client Secret** (obtained previously), and **Scope** (with an optional scope value, email in the examples, but it could be anything else). The call must be made to the proper **token endpoint**. The “grant type” specifies the flow to use – in the examples provided, ‘client_credentials’ denotes **CCF** (**Client Credential Flow**).

[Example in Python](FISHY-ccflow-ex.py)

[Example in Java](FISHY-ccflow-ex.java)

## Installing RabbitMQ
To install the RabbitMQ in a container, running as a daemon, we can use the command:

```docker run -d --hostname rabbit-test --name rabbitmq-simulator -p 8082:15672 -p 5672:5672 rabbitmq:3-management```

In the above command, port 5672 is used for RabbitMQ client connections, and port 8082 is for the RabbitMQ management page.

### Accessing RabbitMQ

We can access the RabbitMQ main page using the URL ```http://localhost:8081```, and using the default username and password, **guest**. Figure 3 shows the main page, from where we can monitor the activity and perform some configurations, like creating queues and logins management (as usual, it is recommended to modify the default administration login).
- **Note**: concerning queues creation, it is unnecessary to perform it from the management site since producers can also make it when sending data.

![Figure 3 - RabbitMQ admin console](images/Figure3.png)

## Framework for testing SPI
We now need a **producer** and a **consumer**to test the complete architecture. The producer will be capturing raw data from the infrastructure. Within the FISHY architecture, this producer is one or more modules at the SIA level. However, since there is no prototype available to work with, we will be using a simple simulator agent that reads real log files, applies the required transformations, and submits the data to the broker after authentication.

The actual [producer code in Python](FISHY-prod-ex.py) is a simpler version. It focuses on the required format transformation from raw data to classified events following the taxonomy under development. To support that transformation, we deploy a simple DB. After, the code exemplifies the interface with the RabbitMQ (we will add authentication later).

The consumer will be integrated with the TIM and SCM modules. Again, since we do not have those prototypes yet, we developed a simulated version of the consumer, aiming to test the RambbitMQ and Keycloak interfaces. Concerning Keycloak, we only need to integrate the functionality described above.

The actual [consumer code in Python](FISHY-cons-ex.py) is also a simpler version. It focuses on the RabbitMQ interface (we will add authentication later).
