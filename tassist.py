import argparse
import scanner
import plot
import pdb
import sys

def check_arg(args=None):
     parser = argparse.ArgumentParser(description=
             'Assistance with daily trading tasks.')
     parser.add_argument('-buy', '--buy',
             nargs=3,
             help='Buy ticker: -buy [ticker] [price] [stop loss]')

     parser.add_argument('-pl', '--plot',
             nargs=1,
             help='Plot ticker: -pl [ticker]')

     parser.add_argument('-s', '--scan',
             nargs=1,
             help='Creates scan list: -s [finviz_best_perf]')

     results = parser.parse_args(args)

     return results.buy, results.plot, results.scan

def main():
    buy_op, plot_op, scan_op = check_arg(sys.argv[1:])

    if buy_op is not None:
        print('Not implemented')
    elif plot_op is not None:
        pass
        plot_ticker = plot.PlotTicker()
        plot_ticker.graph_data(plot_op[0], 12, 22)
    elif scan_op is not None:
       generator = scanner.ListGenerator()
       generator.run()
    else:
        print('Please select required operation.')

if __name__ == '__main__':
    main()
