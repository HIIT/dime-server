package fi.hiit.dime.xdi;

/**
 * This messaging container factory that creates a messaging container for each DiMe user.
 */
/*public class DiMeMessagingContainerFactory extends PrototypingUriMessagingContainerFactory {

	private static final Logger log = LoggerFactory.getLogger(DiMeMessagingContainerFactory.class);

	public DiMeMessagingContainerFactory() {

		super();
	}

	@Override
	public MessagingContainer mountMessagingContainer(UriMessagingContainerRegistry uriMessagingContainerRegistry, String messagingContainerFactoryPath, String requestPath, boolean checkDisabled, boolean checkExpired) throws Xdi2TransportException, Xdi2MessagingException {

		// parse owner

		String ownerString = requestPath.substring(messagingContainerFactoryPath.length());
		if (ownerString.startsWith("/")) ownerString = ownerString.substring(1);
		if (ownerString.contains("/")) ownerString = ownerString.substring(0, ownerString.indexOf("/"));

		XDIAddress ownerXDIAddress;

		try {

			ownerXDIAddress = XDIAddress.create(ownerString);
		} catch (ParserException ex) {

			throw new Xdi2TransportException("Invalid owner string " + ownerString + ": " + ex.getMessage(), ex);
		}

		// find the owner's XDI peer root

		XdiPeerRoot ownerXdiPeerRoot = XdiCommonRoot.findCommonRoot(this.getRegistryGraph()).getPeerRoot(ownerXDIAddress, false);

		if (ownerXdiPeerRoot == null) {

			log.warn("Peer root " + ownerXdiPeerRoot + " not found in the registry graph. Ignoring.");
			return null;
		}

		XdiRoot dereferencedOwnerPeerRoot = ownerXdiPeerRoot.dereference();
		if (dereferencedOwnerPeerRoot instanceof XdiPeerRoot) ownerXdiPeerRoot = (XdiPeerRoot) dereferencedOwnerPeerRoot;

		if (ownerXdiPeerRoot.isSelfPeerRoot()) {

			log.warn("Peer root " + ownerXdiPeerRoot + " is the owner of the registry graph. Ignoring.");
			return null;
		}

		// update the owner

		ownerXDIAddress = ownerXdiPeerRoot.getXDIAddressOfPeerRoot();

		// find the owner's context node

		ContextNode ownerContextNode = this.getRegistryGraph().getDeepContextNode(ownerXDIAddress, true);

		// create and mount the new messaging container

		String messagingContainerPath = messagingContainerFactoryPath + "/" + ownerXDIAddress.toString();

		log.info("Going to mount new messaging container for " + ownerXDIAddress + " at " + messagingContainerPath);

		return super.mountMessagingContainer(uriMessagingContainerRegistry, messagingContainerPath, ownerXDIAddress, ownerXdiPeerRoot, ownerContextNode);
	}

	@Override
	public MessagingContainer updateMessagingContainer(UriMessagingContainerRegistry uriMessagingContainerRegistry, String messagingContainerFactoryPath, String requestPath, boolean checkDisabled, boolean checkExpired, MessagingContainer messagingContainer) throws Xdi2TransportException, Xdi2MessagingException {

		// parse owner

		String ownerString = requestPath.substring(messagingContainerFactoryPath.length());
		if (ownerString.startsWith("/")) ownerString = ownerString.substring(1);
		if (ownerString.contains("/")) ownerString = ownerString.substring(0, ownerString.indexOf("/"));

		XDIAddress ownerXDIAddress = XDIAddress.create(ownerString);

		// find the owner's XDI peer root

		XdiPeerRoot ownerXdiPeerRoot = XdiCommonRoot.findCommonRoot(this.getRegistryGraph()).getPeerRoot(ownerXDIAddress, false);

		if (ownerXdiPeerRoot == null) {

			log.warn("Peer root " + ownerXdiPeerRoot + " no longer found in the registry graph. Going to unmount messaging container.");

			// unmount the messaging container

			uriMessagingContainerRegistry.unmountMessagingContainer(messagingContainer);
			return null;
		}

		// done

		return messagingContainer;
	}

	@Override
	public Iterator<XDIArc> getOwnerPeerRootXDIArcs() {

		Iterator<XdiPeerRoot> ownerPeerRoots = XdiCommonRoot.findCommonRoot(this.getRegistryGraph()).getPeerRoots();

		return new SelectingMappingIterator<XdiPeerRoot, XDIArc> (ownerPeerRoots) {

			@Override
			public boolean select(XdiPeerRoot ownerPeerRoot) {

				if (ownerPeerRoot.isSelfPeerRoot()) return false;
				if (ownerPeerRoot.dereference() != ownerPeerRoot) return false;

				return true;
			}

			@Override
			public XDIArc map(XdiPeerRoot ownerPeerRoot) {

				return ownerPeerRoot.getXDIArc();
			}
		};
	}

	@Override
	public String getRequestPath(String messagingContainerFactoryPath, XDIArc ownerPeerRootXDIArc) {

		XDIAddress ownerXDIAddress = XdiPeerRoot.getXDIAddressOfPeerRootXDIArc(ownerPeerRootXDIArc);

		XdiPeerRoot ownerPeerRoot = XdiCommonRoot.findCommonRoot(this.getRegistryGraph()).getPeerRoot(ownerXDIAddress, false);
		if (ownerPeerRoot == null) return null;

		String requestPath = messagingContainerFactoryPath + "/" + ownerXDIAddress.toString();

		if (log.isDebugEnabled()) log.debug("requestPath for ownerPeerRootXDIArc " + ownerPeerRootXDIArc + " is " + requestPath);

		return requestPath;
	}
}
*/