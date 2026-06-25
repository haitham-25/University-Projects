import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import java.io.IOException;

/**
 * Mapper: extract ArticleID and LANGUAGE.
 * Input: ArticleID, LANGUAGE, AUTHOR, PublicationDate, WordCount, Category, Source, SentimentScore
 * Output Key: LANGUAGE
 * Output Value: IntWritable(1) - used for counting articles per language
 */
public class LanguageMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text language = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // Skip header row if present
        if (key.get() == 0 && value.toString().startsWith("ArticleID")) {
            return;
        }

        String line = value.toString();
        String[] fields = line.split(",");
        
        // Ensure we have at least the required columns (ArticleID, LANGUAGE)
        if (fields.length >= 2) {
            String lang = fields[1].trim();
            if (lang.isEmpty()) {
                lang = "Unknown";
            }
            language.set(lang);
            context.write(language, one);
        } else {
            // Handle malformed lines or unsupported formats
            language.set("Unknown");
            context.write(language, one);
        }
    }
}
