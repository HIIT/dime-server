/*
  Copyright (c) 2015 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

package fi.hiit.dime;

import fi.hiit.dime.authentication.UserCreateForm;
import fi.hiit.dime.authentication.UserService;
import fi.hiit.dime.authentication.Role;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.util.RandomPassword;

import org.junit.After;
import org.junit.Before;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.embedded.EmbeddedWebApplicationContext;
import org.springframework.boot.test.SpringApplicationConfiguration;
import org.springframework.boot.test.TestRestTemplate;
import org.springframework.boot.test.WebIntegrationTest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

/**
 * Base class for REST API testers.
 *
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@SpringApplicationConfiguration(classes = Application.class)
@WebIntegrationTest("server.port:0")
public abstract class RestTest {
    @Autowired
    EmbeddedWebApplicationContext server;

    @Autowired
    UserService userService;

    private String apiBase;

    private RestTemplate rest;

    private User testUser;

    private RandomPassword pw = new RandomPassword();

    @Before 
    public void restSetup() {
	apiBase = String.format("http://localhost:%d/api",
				server.getEmbeddedServletContainer().getPort());
	UserCreateForm form = new UserCreateForm();
	form.setUsername("_testuser_" + pw.getPassword(10, false, false));
	form.setPassword(pw.getPassword(20));
	form.setRole(Role.USER);

	testUser = userService.create(form);

	rest = new TestRestTemplate(form.getUsername(),
				    form.getPassword());

	setup();
    }

    protected void setup() {
    }

    @After
    public void shutdown() {
	userService.removeAllForUserId(testUser.id);
    }

    /**
     * Returns RestTemplate object for performing REST API calls.
     */
    public RestTemplate getRest() {
	return rest;
    }

    /**
     * Construct URL for REST API calls.
     *
     * @param endPoint REST API end point, e.g. /ping
     * @return The constructed full URL, e.g. http://localhost:8080/api/ping
     */
    public String apiUrl(String endPoint) {
	String sep = endPoint.charAt(0) == '/' ? "" : "/";
	return apiBase + sep + endPoint; 
    }

    /**
     * Helper method to check if the REST call was successful.
     */
    public static <T> void assertSuccessful(ResponseEntity<T> res) {
	assert(res.getStatusCode().is2xxSuccessful());
    }
}
