import schedule 
import time 
import Heatmap


def func():
    print("this is python")

def genHeatmap():
    print(f"Running Heatmap now @ {time.strftime('%H:%M')}")
    Heatmap.main(['../../FunctionalSystem/Product-Bazaar-Images/testing'])
    print('done!')

# schedule.every(5).seconds.do(func)
schedule.every(5).minutes.do(genHeatmap)

def main():
    genHeatmap() #test run
    while True:
        schedule.run_pending()
        # time.sleep(1)


if __name__ == '__main__':
    main()