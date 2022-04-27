package modification;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

import org.vizweb.ColorFeatureComputer;
import org.vizweb.QuadtreeFeatureComputer;
import org.vizweb.quadtree.Quadtree;

import static modification.SymmetryFixes.*;
import static modification.BalanceFixes.*;

public class CalculateMetrics {

	/**
	 * A string to go at the top of a file
	 */
	public static String header = "image,colorfulness_1,colorfulness_2"
			+ ",horizontal_balance,horizontal_symmetry,vertical_balance,vertical_symmetry"
			+ ",diagonal_balance,diagonal_symmetry";
	/**
	 * Caculates the main metrics
	 * 
	 * @throws IOException
	 */
	public static String calculateMetrics(String path) throws IOException {
		BufferedImage input = ImageIO.read(new File(path));
		/*******************************
		 * Compute color features
		 *******************************/
		double col1 = 0;
		double col2 = 0;
		
		try {
			col1 = ColorFeatureComputer.computeColorfulness(input);
		} catch (Exception e) {
			//Do nothing
		}
		
		try {
			col2 = ColorFeatureComputer.computeColorfulness2(input);
		} catch (Exception e) {
			//Do nothing
		}

		/*******************************
		 * Compute quadtree features
		 *******************************/
		/*
		 * It could have been beneficial to create an original decomposition strategy.
		 * This would better tailor the library to the needs of this thesis. 
		 */
		Quadtree qtColor = QuadtreeFeatureComputer.getQuadtreeColorEntropy(input);
		
		// Balance style: Eqn
		// Symmetry style: Fix
		
		//Horizontal Vizweb Metrics
		double horizBal = computeHorizontalBalanceEqn(qtColor);
		double horizSym = computeHorizontalSymmetryFix(qtColor);
		//Vertical Vizweb Metrics
		double vertiBal = computeVerticalBalanceEqn(qtColor);
		double vertiSym = computeVerticalSymmetryFix(qtColor);
		//Custom Diagonal Metrics
		double diagBal = computeDiagonalBalanceEqn(qtColor);
		double diagSym = computeDiagonalSymmetryFix(qtColor);
		
		//Testing
		/*
		double horizBal = QuadtreeFeatureComputer.computeHorizontalBalance(qtColor);
		double horizSym = QuadtreeFeatureComputer.computeHorizontalSymmetry(qtColor);
		double vertiBal = QuadtreeFeatureComputer.computeVerticalBalance(qtColor);
		double vertiSym = QuadtreeFeatureComputer.computeVerticalSymmetry(qtColor);
		double diagBal = 1;
		double diagSym = 1;
		*/
		
		double[] arr = {col1, col2, horizBal, horizSym, vertiBal, vertiSym, diagBal, diagSym};
		/*******************************
		 * Get string
		 *******************************/
		StringBuilder sb = new StringBuilder();
		sb.append(path);
		for (double d : arr) {
			if (Double.isNaN(d)) {
				d = 0;
			}
			sb.append(',');
			sb.append(d);
		}
		return sb.toString();
	}
}
