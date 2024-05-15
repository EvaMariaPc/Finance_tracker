import re
import subprocess
from io import BytesIO

import requests

from utils.data import is_list
from utils.datetime_utils import change_datetime_format
from utils.files import read


def pick_destination_folder(*, min_space_percentage):
    free_space = get_partition_free_percentage('/mnt/usb')
    if free_space is not None and free_space >= min_space_percentage:
        return '/mnt/usb/CarOS/videos'
    else:
        return '/CarOS/videos'


def get_partition_free_percentage(partition, logger=None):
    used = subprocess.check_output(f'df -h {partition} | awk \'NR==2 {{print $5}}\'', shell=True).decode().strip()
    if used:
        return 100 - int(used.replace('%', ''))

    if logger:
        logger.warning(f'{partition!r} not found in the output of "df -h"')
    else:
        print(f'{partition!r} not found in the output of "df -h"')

    return None


def split_stream_into_chunks(save_pattern):
    ffmpeg_command = [
        "ffmpeg",
        "-video_size", "1280x720",
        "-framerate", "9",
        "-f", "v4l2",
        "-i", "/dev/video0",
        "-f", "segment",
        "-g", '1',
        "-strftime", "1",
        "-segment_time", "30",
        "-segment_format", "mp4",
        "-reset_timestamps", "1",
        "-force_key_frames", "expr:gte(t,n_forced*30)",  # set the number same as the segment length
        save_pattern]

    subprocess.run(ffmpeg_command, check=True)


def telegram_get_url(path):
    url = read(path, default=None)
    if url is None:
        print(f'File not found: {path!r}')

    return url


def telegram_send(telegram_url, message, logger=None):
    if telegram_url:
        requests.get(telegram_url.format(message))
    elif logger:
        logger.info(f'No telegram url found. Message: {message}')
    else:
        print(f'No telegram url found. Message: {message}')


def get_license_plate_and_datetime_from_path(path):
    try:
        # '(\w{2}-\d{2,3}-\w{3})-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).mp4' -> '<ANYTHING HERE>SB-30-SOM-2022-11-15-10-09-36.mp4'
        license_plate, dt = re.search(r'(\w{2}-\d{2,3}-\w{3})-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).mp4', path).groups()
        dt = change_datetime_format(dt, '%Y-%m-%d-%H-%M-%S', '%Y-%m-%d %H:%M:%S')
        return license_plate, dt
    except Exception:
        pass

    # '(\w{2}-\d{2,3}-\w{3})_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}).mp4' -> '<ANYTHING HERE>SB-30-SOM_2022-11-15_10-09-36.mp4'
    license_plate, dt = re.search(r'(\w{2}-\d{2,3}-\w{3})_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}).mp4', path).groups()
    dt = change_datetime_format(dt, '%Y-%m-%d_%H-%M-%S', '%Y-%m-%d %H:%M:%S')
    return license_plate, dt


def gps_authenticate_car(car_info):
    return requests.post(
        url='https://delta.safefleet.eu/safefleet/api/authenticate_vehicle',
        headers={'Content-Type': 'application/json'},
        json={
            'license_plate': car_info['car_name'],
            'pin': car_info['pin']
        },
        timeout=30
    )


def gps_authenticate_user(car_info):
    return requests.post(
        url='https://delta.safefleet.eu/safefleet/api/authenticate',
        headers={'Content-Type': 'application/json'},
        json={
            'username': car_info['GPS-Platform-User'],
            'password': car_info['GPS-Platform-Pass']
        },
        timeout=30
    )


def gps_authenticate_user_and_car(car_info):
    try:
        auth_user = gps_authenticate_user(car_info)
        auth_car = gps_authenticate_car(car_info)
        error = None
    except Exception as e:
        auth_user = None
        auth_car = None
        error = e

    return auth_user, auth_car, error


def get_car_info(car_database, car_name):
    return read(car_database)[car_name]


def get_gps_safefleet_presence(car_id, start_moment, stop_moment, auth_user):
    url = f'https://delta.safefleet.eu/safefleet/api/vehicles/{car_id}/presences/?start_moment={start_moment}&stop_moment={stop_moment}'
    response = requests.get(url, cookies=auth_user.cookies, timeout=30)
    presences = response.json()

    if is_list(presences) and presences:
        presence = max(presences, key=lambda item: item['moment'])
        return presence['lat'], presence['lng']
    else:
        return None


def get_gps_safefleet_current(car_id, auth_car):
    url = f'https://delta.safefleet.eu/safefleet/api/vehicles/{car_id}'
    response = requests.get(url, cookies=auth_car.cookies, timeout=30)
    response = response.json().get('current_info')

    if response:
        return response['lat'], response['lng']
    else:
        return None


def get_base_coords(car_info):
    return car_info['base-GPS-lat'], car_info['base-GPS-lng']


def get_coords(car_info, start_moment, stop_moment, auth_car, auth_user):
    provider = car_info.get('GPS-Platform-Provider')
    if provider == 'SafeFleet':
        coords = get_gps_safefleet_presence(car_info['vehicle_id'], start_moment, stop_moment, auth_user)

        if coords is None:
            coords = get_gps_safefleet_current(car_info['vehicle_id'], auth_car)
    # elif provider == 'NASA':
    #     raise NotImplementedError
    else:
        raise ValueError(f'Unknown gps provider {provider!r}')

    if coords is None:
        coords = get_base_coords(car_info)

    return coords


def find_mount_point(directory):
    parts = directory.split('/')
    while parts:
        d = '/'.join(parts) or '/'
        cmd = f'df -P {d} | awk \'NR>1 {{print $6}}\''
        mnt = subprocess.check_output(cmd, shell=True).decode().strip()
        if mnt:
            return mnt
        else:
            parts.pop()


def upload_str_as_file(file_path, string, token, data, api_upload):
    """
    file_path is needed even though it's a fake file path, not really used on the local filesystem
    because Amazon requires a filepath
    """
    file_like_object = BytesIO(string.encode())
    response = requests.post(
        url=api_upload,
        headers={'x-auth-token': token},
        files={'photos': (file_path, file_like_object)},
        data=data,
        timeout=60
    )

    if response.status_code == 200:
        return f'Uploaded {file_path}'
    else:
        return (
            f'Upload failed with status code {response.status_code}\n'
            f'Response headers: {response.headers}\n'
            f'Response content: {response.content}\n'
            f'data: {data}\n'
            f'video: {file_path}\n'
        )


def generate_upload_func(api, token, car, file_path):
    def upload(x):
        data = {'lat': 0, 'lng': 0, 'licensePlate': car}
        return upload_str_as_file(file_path, x, token, data, api)

    return upload
from pathlib import Path
from pprint import pprint








import cv2
from pymongo import MongoClient
from tqdm import tqdm

import datetime

from daily_reports import get_offset_from_time, try_s3_download
from utils import s3
from utils.args import ArgParser, time_str
from utils.caros import telegram_send
from utils.datetime_utils import datetime_as_obj, seconds_to_time
from utils.files import delete, mkdir, read, write
from utils.logging_utils import Logger
from utils.misc import (
    get_commit_sha_and_date,
    get_links_and_info_from_mongodb,
    get_time,
    get_video_name,
)
from utils.opencv import get_video_fps, get_video_images, pick_codec, to_BGR

_FILE = __file__.split("/")[-1].split(".")[0]
_LOG = Logger(_FILE, fh_path=f"logs/{_FILE}.log")


def parse_args(argparse_cfg=None, args=None):
    parser = ArgParser(_FILE, argparse_cfg)
    parser.add_argument(
        "--reset",
        action="store_true",
        default=False,
        help="Delete results from previous runs",
    )

    parser.add_argument("--IN", type=str, default=f"runs/{_FILE}/IN", help="The input")
    parser.add_argument(
        "--OUT", type=str, default=f"runs/{_FILE}/OUT", help="The output"
    )
    parser.add_argument("--TMP", type=str, default=f"runs/{_FILE}/TMP", help="Tmp dir")

    parser.add_argument("--s3-bucket", type=str, default="polymore-data")
    parser.add_argument("--mongo-json", type=str, default="secrets/mongo.json")
    parser.add_argument(
        "--filter-car",
        type=str,
        required=True,
        help="List of cars to check. Omit the argument to check all cars",
    )
    parser.add_argument(
        "--filter-date",
        type=str,
        required=True,
        help="The date for which to generate the report Use this format: yyyy-mm-dd",
    )
    parser.add_argument(
        "--filter-start",
        type=time_str,
        default="00:00",
        help="Video time to start analysing from",
    )
    parser.add_argument(
        "--filter-stop",
        type=time_str,
        default="23:59",
        help="Video time to stop analysing at",
    )
    parser.add_argument("--telegram", type=str, help="json with the telegram link")
    return parser.parse_args(args)


def main(ARGS):
    data = find_data(ARGS)
    if not data:
        _LOG.info("No data found. Cancelling merge ...", vars={"args": vars(ARGS)})
        return

    download_videos(ARGS, data)
    dest = merge_videos(ARGS, data)

    if ARGS.telegram:
        telegram = read(ARGS.telegram)
        telegram_send(telegram["url"], f"Merged: {dest}")
        _LOG.info("Sent to telegram")
    else:
        _LOG.info("No telegram")
        _LOG.info(f"Merged: {dest}")


def find_data(ARGS):
    path = f"{ARGS.TMP}/{generate_video_name_from_filters(ARGS)}.json"
    if Path(path).exists():
        data = read(path)
    else:
        data = get_data_from_mongodb(ARGS)
        write(path, data)

    return data


def generate_video_name_from_filters(ARGS):
    start = ARGS.filter_start.replace(":", "")
    stop = ARGS.filter_stop.replace(":", "")
    return f"{ARGS.filter_car}_{ARGS.filter_date}_{start}_{stop}"


def merge_videos(ARGS, data):
    height, width, channels = (720, 1280, 3)
    dest = f"{ARGS.OUT}/{generate_video_name_from_filters(ARGS)}.mp4"
    cc = cv2.VideoWriter_fourcc(*pick_codec(dest))
    video = cv2.VideoWriter(dest, cc, 9, (width, height))
    merged_indexes = set()

    for item in tqdm(data):
        try:
            fps = get_video_fps(item["path"])
            video_start_time = get_real_time(item["time"], 0, fps)
            video_start_idx = get_offset_from_time(video_start_time, fps)
            for v, i, img in get_video_images(item["path"]):
                i_real = video_start_idx + i
                if i_real in merged_indexes:
                    continue

                merged_indexes.add(i_real)
                time = get_real_time(item["time"], i, v.get(cv2.CAP_PROP_FPS))
                img = cv2.putText(
                    img, time, (510, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.75, (0, 255, 0), 3
                )
                video.write(to_BGR(img, "RGB"))
        except Exception as e:
            _LOG.error(exception=e)

    video.release()
    cv2.destroyAllWindows()
    return dest


def get_real_time(video_time, i, fps):
    dt = datetime_as_obj(video_time) + datetime.timedelta(seconds=i / fps)
    return dt.strftime("%H:%M:%S")


def download_videos(ARGS, data):
    bucket = s3.set_bucket(ARGS.s3_bucket)

    for info in tqdm(data):
        if Path(info["path"]).exists():
            continue

        try_s3_download(
            bucket,
            info["video"],
            info["path"],
            skip_if_exists=True,
            error_on_failure=False,
            tries=3,
            logger=_LOG,
        )


def get_data_from_mongodb(ARGS):
    login = read(ARGS.mongo_json)["login"]
    with MongoClient(login) as client:
        video_info = get_links_and_info_from_mongodb(
            client["polyMore"],
            ARGS.filter_car,
            ARGS.filter_date,
            ARGS.filter_start,
            ARGS.filter_stop,
        )

        data = [process_item(it, ARGS.TMP) for it in video_info]
        return sorted(data, key=lambda x: x["time"])


def process_item(x, dir_videos):
    filename = get_video_name(x["link"])

    return {
        "time": get_time(x["link"]),
        "video": filename,
        "path": f"{dir_videos}/{filename}",
    }


def setup(ARGS):
    if ARGS.reset:
        delete(ARGS.OUT)

    mkdir(ARGS.IN)
    mkdir(ARGS.TMP)
    mkdir(ARGS.OUT)


if __name__ == "__main__":
    start = datetime.datetime.now()
    ARGS = parse_args()
    _LOG.debug(vars={"args": vars(ARGS), "git_ref": get_commit_sha_and_date()})

    setup(ARGS)
    main(ARGS)

    end = datetime.datetime.now()
    duration = seconds_to_time((end - start).seconds)
    _LOG.debug(f"{start} -> {end} | {duration}")

