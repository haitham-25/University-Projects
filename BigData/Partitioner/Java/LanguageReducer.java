import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import java.io.IOException;

/**
 * Reducer: Count Articles per LANGUAGE.
 * Since the Combiner will also use this logic, it is implemented as a simple sum.
 * Each reducer will process one LANGUAGE only due to the custom partitioner.
 */
public class LanguageReducer extends Reducer<Text, IntWritable, Text, Text> {
    private Text result = new Text();

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set("Articles: " + sum);
        context.write(key, result);
    }
}
