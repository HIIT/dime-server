package fi.hiit.dime.xdi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.NoSuchBeanDefinitionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.context.support.GenericXmlApplicationContext;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;

import fi.hiit.dime.XdiController;
import fi.hiit.dime.database.ProfileDAO;
import fi.hiit.dime.database.UserDAO;
import xdi2.core.syntax.XDIAddress;
import xdi2.transport.impl.http.HttpTransport;
import xdi2.transport.impl.websocket.WebSocketTransport;
import xdi2.transport.registry.impl.uri.UriMessagingContainerRegistry;

@Service
@Scope("singleton")
public class XdiService {

	private static final Logger log = LoggerFactory.getLogger(XdiController.class);

	public UriMessagingContainerRegistry uriMessagingContainerRegistry;
	public HttpTransport httpTransport;
	public WebSocketTransport webSocketTransport;

	private static XdiService instance = null;
	public UserDAO userDAO = null;
	public ProfileDAO profileDAO = null;

	public static XdiService get() {

		return instance;
	}

	@Autowired
	public XdiService(UserDAO userDAO, ProfileDAO profileDAO) {

		instance = this;
		this.userDAO = userDAO;
		this.profileDAO = profileDAO;

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

	/**
	 * Maps an XDI identifier to a DiMe user ID.
	 * E.g. =!:uuid:e1ea806e-3ecd-4827-adbe-2a76ab178d54 -> e1ea806e-3ecd-4827-adbe-2a76ab178d54
	 */
	public static String userIdFromXDIAddress(XDIAddress userIdXDIArc) {

		return userIdXDIArc.toString().substring("=!:uuid:".length());
	}

	/**
	 * Maps a DiMe user ID to an XDI identifier.
	 * E.g. e1ea806e-3ecd-4827-adbe-2a76ab178d54 -> =!:uuid:e1ea806e-3ecd-4827-adbe-2a76ab178d54
	 */
	public static XDIAddress XDIAddressFromUserId(String userId) {

		return XDIAddress.create("=!:uuid:" + userId);
	}
}
