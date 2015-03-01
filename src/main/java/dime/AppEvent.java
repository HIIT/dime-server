package dime;

import org.springframework.data.annotation.Id;
import java.util.Date;

public class AppEvent {
    @Id
    private String id;
    
    private String name;
    private String eventType;
    private Date time;

    public AppEvent() {}

    public AppEvent(String name, String eventType, Date time) {
	this.name = name;
	this.eventType = eventType;
	this.time = time;
    }

    public String getName() { return name; }
    public String getEventType() { return eventType; }
    public Date getTime() { return time; }
}
