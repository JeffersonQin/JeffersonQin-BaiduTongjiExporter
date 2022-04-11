import baidutongji
import click
import os
import datetime
import json


@click.group()
def cli():
	pass


def save_report(report, name, path):
	with open(os.path.join(path, f'{name}.json'), 'w+', encoding='utf8') as f:
		json.dump(report, f, indent=4, ensure_ascii=False)


def save_all(access_token, site_id, start_date, end_date, start_date2, end_date2, path):
	save_report(baidutongji.getTimeTrendRpt(access_token, site_id, start_date, end_date, baidutongji.TimeTrendRptMetrics().setAllTrue()), 'overview-getTimeTrendRpt', path)
	save_report(baidutongji.getDistrictRpt(access_token, site_id, start_date, end_date, baidutongji.DistrictRptMetrics().setAllTrue()), 'overview-getDistrictRpt', path)
	save_report(baidutongji.getCommonTrackRpt(access_token, site_id, start_date, end_date, baidutongji.CommonTrackRptMetrics().setAllTrue()), 'overview-getCommonTrackRpt', path)
	save_report(baidutongji.getTrendTime(access_token, site_id, start_date, end_date, baidutongji.TrendTimeMetrics().setAllTrue(), start_date2, end_date2), 'trend-time', path)
	save_report(baidutongji.getSourceAll(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'source-all', path)
	save_report(baidutongji.getSourceEngine(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'source-engine', path)
	save_report(baidutongji.getSourceSearchword(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'source-searchword', path)
	save_report(baidutongji.getSourceLink(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'source-link', path)
	save_report(baidutongji.getVisitToppage(access_token, site_id, start_date, end_date, baidutongji.VisitToppageMetrics().setAllTrue(), start_date2, end_date2), 'visit-toppage', path)
	save_report(baidutongji.getVisitLandingpage(access_token, site_id, start_date, end_date, baidutongji.VisitLandingpageMetrics().setAllTrue(), start_date2, end_date2), 'visit-landingpage', path)
	save_report(baidutongji.getVisitTopdomain(access_token, site_id, start_date, end_date, baidutongji.VisitTopdomainMetrics().setAllTrue(), start_date2, end_date2), 'visit-topdomain', path)
	save_report(baidutongji.getVisitDistrict(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'visit-district', path)
	save_report(baidutongji.getVisitWorld(access_token, site_id, start_date, end_date, baidutongji.SourceMetrics().setAllTrue(), start_date2, end_date2), 'visit-world', path)


@cli.command()
@click.option('--access-token', '-t', default=None, help='Access token')
@click.option('--path', '-p', default='.', help='Path to save report')
@click.option('--date', '-d', default=None, help='Date to get report, in form of YYYY-MM-DD of Beijing time')
def fetch(access_token, path, date):
	if access_token is None:
		access_token = os.environ.get('BAIDU_TONGJI_ACCESS_TOKEN')
	if access_token is None:
		raise click.ClickException('Access token is required')

	os.makedirs(path, exist_ok=True)

	# 实时运行，统计的是昨日以及之前
	if date is None:
		SHA_TZ = datetime.timezone(datetime.timedelta(hours=8), name='Asia/Shanghai')

		utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
		beijing_now = utc_now.astimezone(SHA_TZ)

		date = datetime.date(beijing_now.year, beijing_now.month, beijing_now.day)
		date = date - datetime.timedelta(days=1)
	# 指定日期
	else:
		date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

	cron_week = (date.weekday() == 6)
	cron_month = ((date + datetime.timedelta(days=1)).day == 1)
	
	yesterday = date - datetime.timedelta(days=1)

	if cron_week:
		this_week_start = date - datetime.timedelta(days=6)
		this_week_end = date
		last_week_start = this_week_start - datetime.timedelta(days=7)
		last_week_end = this_week_start - datetime.timedelta(days=1)
	
	if cron_month:
		this_month_start = date - datetime.timedelta(days=date.day - 1)
		this_month_end = date
		last_month_end = this_month_start - datetime.timedelta(days=1)
		last_month_start = this_month_start - datetime.timedelta(days=last_month_end.day)

	for site in baidutongji.getSiteList(access_token)['list']:
		domain = site['domain']
		site_id = site['site_id']
		click.echo('Fetching site: {}'.format(domain))

		domain_path = os.path.join(path, domain)
		os.makedirs(domain_path, exist_ok=True)

		# day
		day_path = os.path.join(domain_path, f'day/{date.strftime("%Y%m%d")}')
		print(f'Saving day report to {day_path}')
		os.makedirs(day_path, exist_ok=True)

		save_all(access_token, site_id, date, date, yesterday, yesterday, day_path)

		if date is None:
			# 实时访客
			day_path = os.path.join(domain_path, f'day/{(date + datetime.timedelta(days=1)).strftime("%Y%m%d")}')
			print(f'Saving realtime report to {day_path}')
			os.makedirs(day_path, exist_ok=True)
			save_report(baidutongji.getTrendLatest(access_token, site_id, baidutongji.TrendLatestMetrics().setAllTrue()), 'trend-latest', 
				day_path)

		# week
		if cron_week:
			week_path = os.path.join(domain_path, f'week/{this_week_start.strftime("%Y%m%d")}-{this_week_end.strftime("%Y%m%d")}')
			print(f'Saving week report to {week_path}')
			os.makedirs(week_path, exist_ok=True)
			save_all(access_token, site_id, this_week_start, this_week_end, last_week_start, last_week_end, week_path)

		# month
		if cron_month:
			month_path = os.path.join(domain_path, f'month/{this_month_start.strftime("%Y%m%d")}-{this_month_end.strftime("%Y%m%d")}')
			print(f'Saving month report to {month_path}')
			os.makedirs(month_path, exist_ok=True)
			save_all(access_token, site_id, this_month_start, this_month_end, last_month_start, last_month_end, month_path)


@cli.command()
@click.pass_context
@click.option('--access-token', '-t', default=None, help='Access token')
@click.option('--path', '-p', default='.', help='Path to save report')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']))
def fetch_all(ctx, access_token, path, start_date: click.DateTime, end_date: click.DateTime):
	'''Fetch all history reports by indicating start date and end date in form of YYYY-MM-DD'''
	while start_date <= end_date:
		ctx.invoke(fetch, access_token=access_token, path=path, date=start_date.strftime('%Y-%m-%d'))
		start_date = start_date + datetime.timedelta(days=1)


if __name__ == '__main__':
	cli()
