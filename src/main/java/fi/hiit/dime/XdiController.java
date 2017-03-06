/*
  Copyright (c) 2015-2016 University of Helsinki

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

import java.io.IOException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.NoSuchBeanDefinitionException;
import org.springframework.context.support.GenericXmlApplicationContext;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import xdi2.transport.impl.http.HttpTransport;
import xdi2.transport.impl.http.HttpTransportRequest;
import xdi2.transport.impl.http.HttpTransportResponse;
import xdi2.transport.impl.http.impl.servlet.ServletHttpTransportRequest;
import xdi2.transport.impl.http.impl.servlet.ServletHttpTransportResponse;
import xdi2.transport.impl.websocket.WebSocketTransport;
import xdi2.transport.registry.impl.uri.UriMessagingContainerRegistry;

@Controller
@RequestMapping("/xdi")
public class XdiController {

	private static final Logger log = LoggerFactory.getLogger(XdiController.class);

	private UriMessagingContainerRegistry uriMessagingContainerRegistry;
	private HttpTransport httpTransport;
	private WebSocketTransport webSocketTransport;

	public XdiController() {

		GenericXmlApplicationContext applicationContext = new GenericXmlApplicationContext();
		applicationContext.load(new UrlResource(XdiController.class.getClassLoader().getResource("xdi-applicationContext.xml")));
		applicationContext.refresh();

		this.uriMessagingContainerRegistry = (UriMessagingContainerRegistry) applicationContext.getBean("UriMessagingContainerRegistry");
		if (this.uriMessagingContainerRegistry == null) throw new NoSuchBeanDefinitionException("Required bean 'UriMessagingContainerRegistry' not found.");

		this.httpTransport = (HttpTransport) applicationContext.getBean("HttpTransport");
		if (this.httpTransport == null) throw new NoSuchBeanDefinitionException("Required bean 'HttpTransport' not found.");

		this.webSocketTransport = (WebSocketTransport) applicationContext.getBean("WebSocketTransport");
		if (this.webSocketTransport == null) log.info("Bean 'WebSocketTransport' not found, support for WebSockets disabled.");
		if (this.webSocketTransport != null) log.info("WebSocketTransport found and enabled.");
	}

	@RequestMapping("/**")
	public void service(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) throws IOException {

		httpServletRequest.setCharacterEncoding("UTF-8");
		httpServletResponse.setCharacterEncoding("UTF-8");

		// execute the transport

		HttpTransportRequest request = ServletHttpTransportRequest.fromHttpServletRequest(httpServletRequest, "/xdi");
		HttpTransportResponse response = ServletHttpTransportResponse.fromHttpServletResponse(httpServletResponse);

		this.httpTransport.execute(request, response);
	}
}
