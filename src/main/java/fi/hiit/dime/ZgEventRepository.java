package fi.hiit.dime;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface ZgEventRepository extends MongoRepository<ZgEvent, String> {

    public List<ZgEvent> findAllByOrderByTimestampDesc();
}
