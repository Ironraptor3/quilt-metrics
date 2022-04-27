package modification;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class Main {

	public static void main(String[] args) throws IOException {
		if (args.length > 0) {
			BufferedReader reader = new BufferedReader(new FileReader(args[0]));
			System.out.println(CalculateMetrics.header);
			
			String line = null;
			while ( (line = reader.readLine()) != null) {
				try {
				System.out.println(CalculateMetrics.calculateMetrics(line));
				} catch (Exception e) {
					//Has to fail silently to work correctly
					e.printStackTrace();
				}
			}
			reader.close();
			System.out.println();
		}
	}
}
