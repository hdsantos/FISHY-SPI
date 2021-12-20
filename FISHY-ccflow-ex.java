#CCF example Java  

Packege org.example  
import com.sun.jersey.api.client.Client;  
import com.sun.jersey.api.client.ClientResponse;  
import com.sun.jersey.api.client.WebResource;  
import com.sun.jersey.api.client.config.ClientConfig;  
import com.sun.jersey.api.client.config.DefaultClientConfig;  
import com.sun.jersey.core.util.MultivaluedMapImpl;  
import javax.ws.rs.core.MediaType;  
import javax.ws.rs.core.MultivaluedMap;  
import javax.ws.rs.core.UriBuilder;  

public class Main {  

//URL receives the endpoint 
   private static final String URL= http://localhost:8080/auth/realms/test/protocol/openid-connect/token; 

   public static void main(String[] args) {
      final ClientConfig clientConfig = new DefaultClientConfig();
      Client client = Client.create(clientConfig);                
      MultivaluedMap formData = new MultivaluedMapImpl();
      
      //Parameters for the call
      formData.add"client_id", "java_fishy");
      formData.add"client_secret", "e4ec2b2b-9a69-4a5b-88e6-b0dde3ffc79f");
      formData.add("scope", "email");
      formData.add("grant_type", "client_credentials");
      final WebResource webResource = client.resource(UriBuilder.fromUri(URL).build());
      final ClientResponse clientResponse = webResource.type(MediaType.APPLICATION_FORM_URLENCODED_TYPE).post(ClientResponse.class, formData);

   //Test errors!  
   System.out.println("Response " + clientResponse.getEntity(String.class));           
   }

}
//--get data from server using token in clientResponse
//--process it
//--repeat auntil required
