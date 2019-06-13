import { Component, ElementRef, Input, OnChanges, OnInit, ViewChild, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import * as _ from "lodash";

import { AggregateResult } from '../models/index';
import { BarChartComponent } from './barchart.component';

@Component({
    selector: 'ia-term-frequency',
    templateUrl: './term-frequency.component.html',
    styleUrls: ['./term-frequency.component.scss']
})
export class TermFrequencyComponent extends BarChartComponent implements OnInit, OnChanges {
    @ViewChild('termfrequency') private termFreqContainer: ElementRef;
    @Input() searchData: AggregateResult[];
    @Input() visualizedField;
    @Input() asPercent: boolean = false;

    private xBarWidth: number;
    private xBarHalf: number;
    private tooltip: any;
    private maxCategories: number = 30;

    ngOnInit() {
    }

    ngOnChanges(changes: SimpleChanges) {
        if (this.chartElement == undefined) {
            this.chartElement = this.termFreqContainer.nativeElement;
            this.calculateCanvas();
        }
        // redraw only if searchData changed
        if (changes['searchData'] != undefined && changes['searchData'].previousValue != changes['searchData'].currentValue) {
            this.prepareTermFrequency();
            this.setupYScale();
            this.createChart(this.visualizedField.displayName, this.searchData.length);
            this.rescaleY(this.asPercent);
            this.setupBrushBehaviour();
            this.drawChartData();
            this.setupTooltip();
        }

        //listen for changes in 'asPercent'
        else if (changes['asPercent'] != undefined) {
            if (changes['asPercent'].previousValue != changes['asPercent'].currentValue) {
                this.rescaleY(this.asPercent);
            }
        }
    }

    prepareTermFrequency() {
        if (typeof this.searchData[0].key === "number") {
            this.searchData = _.sortBy(this.searchData, d => d.key);
        }
        this.xDomain = [-.5, this.searchData.length - .5];
        this.calculateBarWidth(this.searchData.length);
        this.xScale = d3.scaleLinear().domain(this.xDomain).rangeRound([0, this.width]);
        this.yMax = d3.max(this.searchData.map(d => d.doc_count));
        this.totalCount = _.sumBy(this.searchData, d => d.doc_count);
    }

    calculateBarWidth(noCategories) {
        this.xBarWidth = .95 * this.width / noCategories;
        this.xBarHalf = this.xBarWidth / 2;
    }


    drawChartData() {
        /**
        * bind data to chart, remove or update existing bars, add new bars
        */

        const update = this.chart
            .selectAll('.bar')
            .attr('clip-path', 'url(#my-clip-path)')
            .data(this.searchData);

        // remove exiting bars
        update.exit().remove();

        this.xAxisClass.tickValues(this.searchData.map(d => d.key)).tickFormat(d3.format("s"));
        // x axis ticks
        this.xAxis.selectAll('text')
            .data(this.searchData)
            .text(d => d.key)
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-35)");

        // update existing bars
        this.chart.selectAll('.bar').transition()
            .attr('x', (d, i) => this.xScale(i) - this.xBarHalf)
            .attr('y', d => this.yScale(d.doc_count))
            .attr('width', this.xBarWidth)
            .attr('height', d => this.height - this.yScale(d.doc_count));


        if (this.searchData.length > this.maxCategories) {
            // remove x axis ticks
            this.xAxis.selectAll(".tick").remove();

            // add new bars
            update
                .enter()
                .append('rect')
                .attr('class', 'bar')
                .attr('x', (d, i) => this.xScale(i) - this.xBarHalf)
                .attr('width', this.xBarWidth)
                .attr('y', this.yScale(0)) //set to zero first for smooth transition
                .attr('height', 0)
                .transition().duration(750)
                .delay((d, i) => i * 10)
                .attr('y', d => this.yScale(d.doc_count))
                .attr('height', d => this.height - this.yScale(d.doc_count))

            // add tooltips
            this.chart.selectAll(".bar")
                .on("mouseover", (d,i) => {
                    var yPos = this.height + 5 * this.margin.top;
                    var xPos = this.xScale(i);
                    this.tooltip
                        .text(d.key)
                        .style("left", xPos + "px")
                        .style("top", yPos + "px")
                        .style("visibility", "visible")
                })
                .on("mouseout", () => this.tooltip.style("visibility", "hidden"))
        }

        else {
            // add new bars, without tooltips
            update
                .enter()
                .append('rect')
                .attr('class', 'bar')
                .attr('x', (d, i) => this.xScale(i) - this.xBarHalf)
                .attr('width', this.xBarWidth)
                .attr('y', this.yScale(0)) //set to zero first for smooth transition
                .attr('height', 0)
                .transition().duration(750)
                .delay((d, i) => i * 10)
                .attr('y', d => this.yScale(d.doc_count))
                .attr('height', d => this.height - this.yScale(d.doc_count))
        }
    }

    setupTooltip() {
        // select the tooltip in the template
        this.tooltip = d3.select(".tooltip");
    }


    zoomIn() {
        let selection = this.searchData.filter((d, i) => i >= this.xScale.domain()[0] && i <= this.xScale.domain()[1]);
        this.calculateBarWidth(selection.length + 1);

        this.chart.selectAll('.bar')
            .transition().duration(750)
            .attr('x', (d, i) => this.xScale(i) - this.xBarHalf)
            .attr('y', d => this.yScale(d.doc_count))
            .attr('width', this.xBarWidth);

        this.xAxis
            .call(d3.axisBottom(this.xScale).ticks(selection.length))
            .selectAll('.tick text')
            .text((d, i) => selection[i].key)
            .attr("text-anchor", "right")
            .attr("transform", "rotate(-35)");  
    }

    zoomOut() {
        this.xDomain = [-.5, this.searchData.length - .5];
        this.calculateBarWidth(this.searchData.length);
        this.xScale = d3.scaleLinear().domain(this.xDomain).rangeRound([0, this.width]);
        this.xAxis
            .call(d3.axisBottom(this.xScale).ticks(this.searchData.length));
        this.drawChartData();
    }

}
