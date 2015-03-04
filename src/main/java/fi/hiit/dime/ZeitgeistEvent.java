package fi.hiit.dime;

import org.springframework.data.annotation.Id;
import java.util.Date;

public class ZeitgeistEvent {
    @Id
    private String id;

    private String actor;

    private String manifestation;
    private String interpretation;

    private String origin;
    private Date timestamp;

    private String payload;

    private ZeitgeistSubject subject;

    public ZeitgeistEvent() {}

    public ZeitgeistEvent(String id,
			  String actor, 
			  String manifestation, 
			  String interpretation,
			  String origin,
			  Date timestamp,
			  String payload,
			  ZeitgeistSubject subject) {
	this.id = id;
    	this.actor = actor;
    	this.manifestation = manifestation;
	this.interpretation = interpretation;
	this.origin = origin;
    	this.timestamp = timestamp;
	this.payload  = payload;
	this.subject = subject;
    }

    public String getId() { return id; }
    public String getActor() { return actor; }
    public String getManifestation() { return manifestation; }
    public String getInterpretation() { return interpretation; }
    public String getOrigin() { return origin; }
    public Date getTimestamp() { return timestamp; }
    public String getPayload() { return payload; }
    public ZeitgeistSubject getSubject() { return subject; }
}
