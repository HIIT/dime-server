package fi.hiit.dime.data;

import org.springframework.data.annotation.Id;
import java.util.Date;

public class ZgSubject {
    @Id
    private String id;

    private String uri;
    private String manifestation;
    private String interpretation;
    private String mimetype;
    private String storage;
    private String text;

    public ZgSubject() {}

    public ZgSubject(String id,
			    String uri,
			    String manifestation,
			    String interpretation,
			    String mimetype,
			    String storage,
			    String text) {
	this.id = id;
	this.uri = uri;
	this.manifestation = manifestation;
	this.interpretation = interpretation;
	this.mimetype = mimetype;
	this.storage = storage;
	this.text = text;
    }

    public String getId() { return id; }
    public String getUri() { return uri; }
    public String getManifestation() { return manifestation; }
    public String getInterpretation() { return interpretation; }
    public String getMimetype() { return mimetype; }
    public String getStorage() { return storage; }
    public String getText() { return text; }

    public boolean isStub() {
	return uri == null || uri.isEmpty();
    }
}
