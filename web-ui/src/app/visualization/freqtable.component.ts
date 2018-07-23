import { Input, Component, OnInit, OnChanges, ElementRef, ViewEncapsulation, SimpleChanges } from '@angular/core';
import { TitleCasePipe } from '@angular/common';

import * as d3 from 'd3';
import * as _ from "lodash";
import { TableBody } from '../../../node_modules/primeng/primeng';

@Component({
  selector: 'freqtable',
  templateUrl: './freqtable.component.html',
  styleUrls: ['./freqtable.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class FreqtableComponent implements OnChanges {
  @Input('searchData')
  public searchData: {
    key: any,
    doc_count: number,
    key_as_string?: string
  }[];
  @Input() public visualizedField;
  @Input() public chartElement;

  private yAsPercent: boolean = false;
  private yTicks: number = 10;
  private xTickValues: string[];
  private margin = { top: 10, bottom: 120, left: 70, right: 10 };
  // private svg: any;
  private chart: any;
  private width: number;
  private height: number;
  private xScale: d3.ScaleBand<string>;
  private yScale: d3.ScaleLinear<number, number>;
  private xAxis: d3.Selection<any, any, any, any>;
  private yAxis: d3.Selection<any, any, any, any>;
  private yMax: number;
  private xDomain: Array<string>;
  private yDomain: Array<number>;
  private yAxisLabel: any;
  private update: any;

  private svg: any;
  private table: any;

  constructor(private titlecasepipe: TitleCasePipe) { }

  ngOnChanges(changes: SimpleChanges) {
    if (this.searchData && this.visualizedField) {
      // date fields are returned with keys containing identifiers by elasticsearch
      // replace with string representation, contained in 'key_as_string' field
      if ('key_as_string' in this.searchData[0]) {
        this.searchData.forEach(cat => cat.key = cat.key_as_string)
      }
      this.calculateDomains();
      if (changes['visualizedField'] != undefined) {
        // this.createChart(changes['visualizedField'].previousValue != changes['visualizedField'].currentValue);
        // this.drawChartData();
        // this.setScale();
        this.createTable(changes['visualizedField'].previousValue != changes['visualizedField'].currentValue);
      }
    }
  }

  calculateDomains() {
    /**
     adjust the x and y ranges
     */
    this.xDomain = this.searchData.map(d => d.key);
    this.yMax = d3.max(this.searchData.map(d => d.doc_count));
    this.yDomain = this.yAsPercent ? [0, 1] : [0, this.yMax];
    this.yTicks = (this.yDomain[1] > 1 && this.yDomain[1] < 20) ? this.yMax : 10;
    this.xTickValues = this.xDomain.length > 30 ? this.xDomain.filter((d, i) => i % 10 == 0) : this.xDomain;
  }

  setScale() {
    /**
    * if the user selects percentage / count display,
    * - rescale y values & axis
    * - change axis label and ticks
    */
    this.calculateDomains();
    this.yScale.domain(this.yDomain);

    let totalCount = _.sumBy(this.searchData, d => d.doc_count);
    let preScale = this.yAsPercent ? d3.scaleLinear().domain([0, totalCount]).range([0, 1]) : d3.scaleLinear();

    this.chart.selectAll('.bar')
      .transition()
      .attr('y', d => this.yScale(preScale(d.doc_count)))
      .attr('height', d => this.height - this.yScale(preScale(d.doc_count)));

    let tickFormat = this.yAsPercent ? d3.format(".0%") : d3.format("d");
    let yAxis = d3.axisLeft(this.yScale).ticks(this.yTicks).tickFormat(tickFormat)
    this.yAxis.call(yAxis);

    let yLabelText = this.yAsPercent ? "Percent" : "Frequency";
    this.yAxisLabel.text(yLabelText);
  }
  /**
   * Creates the chart to draw the data on (including axes and labels).
   * @param forceRedraw Erases the current chart and create a new one.
   */
  createTable(forceRedraw: boolean) {
    /**
    * select DOM elements, set up scales and axes
    */
    if (this.svg) {
      this.svg.remove();
    }

    this.svg = d3.select(this.chartElement).append('div')
      .attr("id", "table-div")
      .attr('width', this.chartElement.offsetWidth)
      .attr('height', this.chartElement.offsetHeight);
    this.width = this.chartElement.offsetWidth - this.margin.left - this.margin.right;
    this.height = this.chartElement.offsetHeight - this.margin.top - this.margin.bottom;

    // this.svg.selectAll('g').remove();
    // this.svg.selectAll('text').remove();
    // chart plot area
    // this.table = d3.select(".svg").append('table')
    this.table = d3.select("#table-div").append("table")
    this.table.attr("class", "table table-hover")
    var header = this.table.append('thead').append('tr')

    var rowsArray = [];

    for (var field of this.searchData) {
      if (field.key_as_string != undefined) {
        rowsArray.push([field.key_as_string, field.doc_count]);
      }
      else {
        rowsArray.push([field.key, field.doc_count]);
      }
    }

    header
      .selectAll('th')
      .data([this.titlecasepipe.transform(this.visualizedField), 'Frequency'])
      .enter()
      .append('th')
      .text(function (d) { return d })

    var tablebody = this.table.append("tbody");
    var rows = tablebody
      .selectAll("tr")
      .data(rowsArray)
      .enter()
      .append("tr");

    var cells = rows.selectAll("td")
      // each row has data associated; we get it and enter it for the cells.
      .data(function (d) {
        console.log(d);
        return d;
      })
      .enter()
      .append("td")
      .text(function (d) {
        return d;
      });
  }


  /**
   * Creates the chart to draw the data on (including axes and labels).
   * @param forceRedraw Erases the current chart and create a new one.
   */
  createChart(forceRedraw: boolean) {
    /**
    * select DOM elements, set up scales and axes
    */
    if (this.svg) {
      this.svg.remove();
    }

    this.svg = d3.select(this.chartElement).append('svg')
      .attr('width', this.chartElement.offsetWidth)
      .attr('height', this.chartElement.offsetHeight);
    this.width = this.chartElement.offsetWidth - this.margin.left - this.margin.right;
    this.height = this.chartElement.offsetHeight - this.margin.top - this.margin.bottom;

    this.svg.selectAll('g').remove();
    this.svg.selectAll('text').remove();
    // chart plot area
    this.chart = this.svg.append('g')
      .attr('class', 'bars')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

    this.xScale = d3.scaleBand().domain(this.xDomain).rangeRound([0, this.width]).padding(.1);
    this.yScale = d3.scaleLinear().domain(this.yDomain).range([this.height, 0]);

    this.xAxis = this.svg.append('g')
      .attr('class', 'axis x')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top + this.height})`)
      .call(d3.axisBottom(this.xScale).tickValues(this.xTickValues));

    // set style of x tick marks
    this.xAxis.selectAll('text')
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-35)");

    this.yAxis = this.svg.append('g')
      .attr('class', 'axis y')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)
      .call(d3.axisLeft(this.yScale).ticks(this.yTicks).tickFormat(d3.format("d")));

    // adding axis labels
    let xLabelText = this.visualizedField.replace(/\b\w/g, l => l.toUpperCase());
    let yLabelText = "Frequency";

    this.svg.append("text")
      .attr("class", "xlabel")
      .attr("text-anchor", "middle")
      .attr("x", this.width / 2)
      .attr("y", this.height + this.margin.bottom)
      .text(xLabelText);

    this.yAxisLabel = this.svg.append("text")
      .attr("class", "ylabel")
      .attr("text-anchor", "middle")
      .attr("y", this.margin.top + this.height / 2)
      .attr("x", this.margin.left / 2)
      .attr("transform", `rotate(${-90} ${this.margin.left / 3} ${this.margin.top + this.height / 2})`)
      .text(yLabelText);
  }

  drawChartData() {
    /**
    * bind data to chart, remove or update existing bars, add new bars
    */

    const update = this.chart.selectAll('.bar')
      .data(this.searchData);

    // remove exiting bars
    update.exit().remove();

    // update existing bars
    this.chart.selectAll('.bar').transition()
      .attr('x', d => this.xScale(d.key))
      .attr('y', d => this.yScale(d.doc_count))
      .attr('width', this.xScale.bandwidth())
      .attr('height', d => this.height - this.yScale(d.doc_count));

    // add new bars
    update
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => this.xScale(d.key))
      .attr('width', this.xScale.bandwidth())
      .attr('y', d => this.yScale(0)) //set to zero first for smooth transition
      .attr('height', 0)
      .transition()
      .delay((d, i) => i * 10)
      .attr('y', d => this.yScale(d.doc_count))
      .attr('height', d => this.height - this.yScale(d.doc_count));

  }

}


type KeyFrequencyPair = {
  key: string;
  doc_count: number;
  key_as_string?: string;
}
