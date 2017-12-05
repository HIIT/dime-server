/*
  Copyright (c) 2016-2017 University of Helsinki

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
package fi.hiit.dime.xdi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import xdi2.core.features.nodetypes.XdiPeerRoot;
import xdi2.core.syntax.XDIAddress;
import xdi2.core.syntax.XDIArc;
import xdi2.core.syntax.parser.ParserException;
import xdi2.messaging.container.MessagingContainer;
import xdi2.messaging.container.exceptions.Xdi2MessagingException;
import xdi2.messaging.container.factory.impl.uri.PrototypingUriMessagingContainerFactory;
import xdi2.transport.exceptions.Xdi2TransportException;
import xdi2.transport.registry.impl.uri.UriMessagingContainerRegistry;

/**
 * This messaging container factory that creates a messaging container for each DiMe profile.
 */
public class DiMeMessagingContainerFactory extends PrototypingUriMessagingContainerFactory {

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

        // check if a profile with DID exists

        boolean exists = XdiService.findProfileByDidXDIAddress(ownerXDIAddress) != null;
        if (! exists) return null;

        // create and mount the new messaging container

        String messagingContainerPath = messagingContainerFactoryPath + "/" + ownerXDIAddress.toString();

        log.info("Will create messaging container for " + ownerXDIAddress + " at " + messagingContainerPath);

        return super.mountMessagingContainer(uriMessagingContainerRegistry, messagingContainerPath, ownerXDIAddress, null, null);
    }

    @Override
    public MessagingContainer updateMessagingContainer(UriMessagingContainerRegistry uriMessagingContainerRegistry, String messagingContainerFactoryPath, String requestPath, boolean checkDisabled, boolean checkExpired, MessagingContainer messagingContainer) throws Xdi2TransportException, Xdi2MessagingException {

        return messagingContainer;
    }

    @Override
    public String getRequestPath(String messagingContainerFactoryPath, XDIArc ownerPeerRootXDIArc) {

        XDIAddress ownerXDIAddress = XdiPeerRoot.getXDIAddressOfPeerRootXDIArc(ownerPeerRootXDIArc);

        String requestPath = messagingContainerFactoryPath + "/" + ownerXDIAddress.toString();

        if (log.isDebugEnabled()) log.debug("requestPath for ownerPeerRootXDIArc " + ownerPeerRootXDIArc + " is " + requestPath);

        return requestPath;
    }
}
