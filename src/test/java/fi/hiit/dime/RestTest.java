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

import fi.hiit.dime.authentication.Role;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.authentication.UserCreateForm;
import fi.hiit.dime.authentication.UserService;
import fi.hiit.dime.data.*;
import fi.hiit.dime.util.RandomPassword;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.After;
import org.junit.Before;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.embedded.EmbeddedWebApplicationContext;
import org.springframework.boot.test.SpringApplicationConfiguration;
import org.springframework.boot.test.TestRestTemplate;
import org.springframework.boot.test.WebIntegrationTest;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.client.RestTemplate;
import static org.junit.Assert.*;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

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

    @Autowired 
    private ObjectMapper objectMapper;

    private String apiBase;

    private RestTemplate rest;

    private User testUser;

    private RandomPassword pw = new RandomPassword();

    public static String randomText = "Aliquam erat volutpat.  Nunc eleifend leo vitae magna.  In id erat non orci commodo lobortis.  Proin neque massa, cursus ut, gravida ut, lobortis eget, lacus.  Sed diam.  Praesent fermentum tempor tellus.  Nullam tempus.  Mauris ac felis vel velit tristique imperdiet.  Donec at pede.  Etiam vel neque nec dui dignissim bibendum.  Vivamus id enim.  Phasellus neque orci, porta a, aliquet quis, semper a, massa.  Phasellus purus.  Pellentesque tristique imperdiet tortor.  Nam euismod tellus id erat.";

    protected String eventApi, eventsApi, infoElemApi, infoElemsApi;

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
        eventApi = apiUrl("/data/event");
        eventsApi = apiUrl("/data/events");
        infoElemApi = apiUrl("/data/informationelement");
        infoElemsApi = apiUrl("/data/informationelements");
    }

    @After
    public void shutdown() {
        userService.removeAllForUserId(testUser.getId());
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

    /**
     * Helper method to check if the REST call caused an HTTP 4xx error.
     */
    public static <T> void assertClientError(ResponseEntity<T> res) {
        assert(res.getStatusCode().is4xxClientError());
    }

    protected Message createTestEmail() {
        return createTestEmail("Hello, world", "Hello DiMe!");
    }

    protected Person createPerson(String firstName, String lastName, String email) {
        Person p = new Person();
        p.firstName = firstName;
        p.lastName = lastName;
        p.emailAccount = email;

        return p;
    }

    protected String personToStr(Person p) {
        return String.format("%s %s <%s>", p.firstName, p.lastName, p.emailAccount);
    }

    protected Message createTestEmail(String content, String subject) {
        // Create a message
        Message msg = new Message();
        msg.date = new Date(); // current date
        msg.subject = subject;

        msg.from = createPerson("Mats", "Sjöberg", "mats.sjoberg@helsinki.fi");
        msg.fromString = personToStr(msg.from);

        msg.to = new ArrayList<Person>();
        msg.to.add(createPerson("Mats", "Sjöberg", "mats.sjoberg@hiit.fi"));
        msg.toString = personToStr(msg.to.get(0));

        msg.cc = new ArrayList<Person>();
        msg.cc.add(createPerson("Mats", "Sjöberg", "mats.sjoberg@cs.helsinki.fi"));
        msg.ccString = personToStr(msg.cc.get(0));

        msg.plainTextContent = content;
        
        SimpleDateFormat format =
            new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss Z");
        
        msg.rawMessage = 
            "From: " + msg.fromString + "\n" +
            "To: " + msg.toString + "\n" +
            "Cc: " + msg.ccString + "\n" + 
            "Subject: " + msg.subject + "\n" +
            "Date: " + format.format(msg.date) +
            "Message-ID: <43254843985749@helsinki.fi>\n" + 
            "\n\n" + msg.plainTextContent;

        return msg;
    }

    

    protected ScientificDocument createScientificDocument(String someText) {
        ScientificDocument doc = new ScientificDocument();
        doc.mimeType = "application/pdf";
        doc.title = "Microsoft Word - paper.docx";
        doc.plainTextContent = someText;
        doc.uri = "/home/testuser/docs/memex_iui2016_submittedversion.pdf";
        doc.firstPage = 0;
        doc.lastPage = 0;
        doc.year = 0;
        doc.type = "http://www.hiit.fi/ontologies/dime/#ScientificDocument";

        Person a1 = new Person();
        a1.firstName = "Matti";
        a1.lastName = "Meikäläinen";
        a1.middleNames = Arrays.asList("M.");

        Person a2 = new Person();
        a2.firstName = "John";
        a2.middleNames = Arrays.asList("Albert", "Bob");
        a2.lastName = "Doe";

        doc.authors = new ArrayList<Person>();
        doc.authors.add(a1);
        doc.authors.add(a2);
        
        doc.keywords = Arrays.asList("foo", "bar", "baz");

        return doc;
    }

    protected ReadingEvent createReadingEvent(InformationElement doc,
                                              String content) 
    {
        ReadingEvent re = new ReadingEvent();
        fillReadingEvent(re, doc, content);
        return re;
    }

    protected void fillReadingEvent(ReadingEvent re, InformationElement doc,
                                    String content) {
        re.targettedResource = doc;

        re.type = "http://www.hiit.fi/ontologies/dime/#ReadingEvent";
        re.plainTextContent = content;
        re.pageNumbers = Arrays.asList(0, 4);

        final int numEyeData = 10;
        List<PageEyeData> eyeData = new ArrayList<PageEyeData>();
        for (int i=0; i<numEyeData; i++) {
            PageEyeData ed = new PageEyeData();
            ed.Xs = Arrays.asList(i*0.0, i*1.5, i*2.2);
            ed.Ys = Arrays.asList(i*0.0, i*1.5, i*2.2);
            ed.Ps = Arrays.asList(i*0.0, i*1.5, i*2.2);

            ed.startTimes = Arrays.asList(i*1l, i*2l, i*4l);
            ed.endTimes = Arrays.asList(i+1l, i*2+1l, i*4+2l);

            ed.durations = Arrays.asList(1l, 1l, 2l);

            ed.pageIndex = i;

            ed.scaleFactor = 1.685;
            eyeData.add(ed);
        }

        re.pageEyeData = eyeData;

        assertEquals(numEyeData, re.pageEyeData.size());

        List<Rect> rs = new ArrayList<Rect>();
        Rect r = new Rect();
        r.origin = new Point(0.0, 453.5);
        r.readingClass = Rect.CLASS_VIEWPORT;
        r.pageIndex = 0;
        r.scaleFactor = 1.685;
        r.classSource = 1;
        r.size = new Size(612.0, 338.5);
        rs.add(r);
        re.pageRects = rs;
    }

    /**
     * Helper method to print out the content of a DiMeData object.
     */
    protected void dumpData(String message, Object data) {
        try {
            System.out.println(message + "\n" +
                               objectMapper.writerWithDefaultPrettyPrinter().
                               writeValueAsString(data));
        } catch (IOException e) {
        }
    }

    /**
     * Helper method to print out the content of an array of DiMeData objects.
     */
    protected void dumpData(String message, Object[] data) {
        try {
            for (int i=0; i<data.length; i++) {
                String dataStr = objectMapper.
                    writerWithDefaultPrettyPrinter().writeValueAsString(data[i]);
                System.out.println(String.format("%s [%d]: %s", message, i, dataStr));
            }
        } catch (IOException e) {
        }
    }

    // Uploading helpers
    
    protected <T extends InformationElement> T 
                         uploadElement(T elem, Class<T> responseType) 
    {
        return uploadData(infoElemApi, elem, responseType);
    }

    protected <T extends InformationElement> T[] 
                         uploadInformationElements(T[] elems,
                                                   Class<T[]> responseType) 
    {
        return uploadData(infoElemsApi, elems, responseType);
    }

    protected <T extends Event> T uploadEvent(T event, Class<T> responseType) {
        return uploadData(eventApi, event, responseType);
    }

    protected <T extends Event> T[] uploadEvents(T[] events,
                                                 Class<T[]> responseType) {
        return uploadData(eventsApi, events, responseType);
    }

    protected <S, T> T uploadData(String apiUrl, S data, Class<T> responseType) {
        try {
            // Upload to DiMe
            ResponseEntity<T> res = getRest().postForEntity(apiUrl, data, 
                                                            responseType);

            // Check that HTTP status was as expected
            if (responseType == ApiError.class)
                assertClientError(res);
            else
                assertSuccessful(res);
            
            return res.getBody();

        } catch (HttpMessageNotReadableException ex) {
            System.out.println(ex);

            ResponseEntity<ApiError> res =
                getRest().postForEntity(apiUrl, data, ApiError.class);
            System.out.println(res.getBody());

            fail();
        }
        return null;
    }


    // Downloading helpers

    protected ApiError getDataExpectError(String apiUrl) {
        return getData(apiUrl, ApiError.class);
    }

    protected <T> T getData(String apiUrl, Class<T> responseType) {
        try {
            ResponseEntity<T> res = getRest().getForEntity(apiUrl, responseType);

            // Check that HTTP was as expected
            if (responseType == ApiError.class)
                assertClientError(res);
            else
                assertSuccessful(res);

            return res.getBody();
        } catch (HttpMessageNotReadableException ex) {
            System.out.println(ex);

            ResponseEntity<ApiError> res =
                getRest().getForEntity(apiUrl, ApiError.class);
            System.out.println(res.getBody());

            fail();
        }
        return null;
    }

    protected <T extends Event> T getEvent(long id, Class<T> responseType) {
        return getData(eventApi + "/" + id, responseType);
    }

    protected <T extends InformationElement> T getElement(long id, Class<T> responseType) {
        return getData(infoElemApi + "/" + id, responseType);
    }

    protected static class ApiError {
        public Long timestamp;   // 1450449761533
        public Integer status;   // 400
        public String error;     // "Bad Request"
        public String exception; // "fi.hiit.dime.AuthorizedController$BadRequestException"
        public String message;   // longer message...
        public String path;      // "/api/data/informationelement"

        @Override 
        public String toString() {
            return "Error " + status + ": " + error + " [" + path + "] " + 
                exception + ": " + message;
        }
    }
}
